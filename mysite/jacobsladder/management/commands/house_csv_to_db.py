from django.core.management.base import BaseCommand
from ... import base_code, folder_reader, house, place, service


class Command(BaseCommand, base_code.BaseCode):
    PREFERENCE_VOTE_KIND = 'Preference Count'
    help = 'Add elections from csv files'

    def __call__(self, election_year, folder, pref_objects, round_objects):
        booths_directory, house_election, preference_distribution_directory, \
            seats_directory, two_candidate_preferred_directory, \
            types_directory = self.start_election(election_year, folder)
        self.setup(booths_directory, house_election, seats_directory,
                   two_candidate_preferred_directory, types_directory)
        self.first_pass_preferences(house_election, pref_objects,
                                    preference_distribution_directory,
                                    round_objects)
        self.second_pass_preferences(house_election, pref_objects,
                                     preference_distribution_directory)

    def first_pass_preferences(self, house_election, pref_objects,
                               preference_distribution_directory,
                               round_objects,
                               text_to_print="First Pass: Reading files in "
                                             "preference distribution "
                                             "directory", quiet=False):
        folder_reader.FolderReader.echo(quiet, text_to_print, False)
        for filename in folder_reader.FolderReader.walk(
                preference_distribution_directory):
            with open(filename, "r") as in_file:
                Command.set_all_preferences(house_election, pref_objects,
                                            self.fetch_reader(filename,
                                                              in_file),
                                            round_objects)

    def second_pass_preferences(self, house_election, pref_objects,
                                preference_distribution_directory,
                                text_to_print="Second Pass: Reading files in "
                                              "preference distribution "
                                              "directory", quiet=False):
        folder_reader.FolderReader.echo(quiet, text_to_print)
        for filename in folder_reader.FolderReader.walk(
                preference_distribution_directory):
            with open(filename, "r") as in_file:
                reader = self.fetch_reader(filename, in_file)
                while True:
                    try:
                        Command.transfer_if_preference(house_election,
                                                       pref_objects, reader)
                    except StopIteration:
                        folder_reader.FolderReader.echo(quiet, "", False)
                        break

    def handle(self, *arguments, **keywordarguments):
        pref_objects = house.CandidatePreference.objects
        round_objects = house.PreferenceRound.objects
        election_items = Command.get_election_items()
        [self(election_year, folder, pref_objects, round_objects) for
         election_year, folder in election_items]

    @staticmethod
    def fetch_transfer_data(current_round_numb, house_election, reader, row):
        candidate, received, seat = Command.fetch_candid(house_election, row)
        transferred = Command.advance(reader)
        return candidate, house.PreferenceRound.objects.get(
            seat=seat, election=house_election,
            round_number=current_round_numb), received, received, seat, \
               transferred

    @staticmethod
    def transfer_if_preference(house_election, pref_objects, reader):
        row = next(reader)
        if row[Command.KIND_OF_VOTES_HEADER] == Command.PREFERENCE_VOTE_KIND:
            if int(row[Command.NUMBER_OF_VOTES_HEADER]) > 0:
                Command.transfer(house_election, pref_objects, reader, row)

    @staticmethod
    def add_one_tally(house_election, row):
        candidate, seat = Command.find_candidate_for_seat(house_election, row)
        booth_attributes = {'name': row[Command.BOOTH_NAME_HEADER],
                            'seat': seat}
        booth = Command.fetch_by_aec_code(
            booth_attributes, place.Booth.objects, place.BoothCode.objects,
            'booth', int(row[Command.BOOTH_CODE_HEADER]))
        try:
            Command.get_two_candidate_pref_votes(booth, candidate,
                                                 house_election, row)
        except house.VoteTally.DoesNotExist:
            print("house_election", house_election)
            print("house_election.pk", house_election.pk)
            print("row", row)
            print("seat", seat)
            print("seat.pk", seat.pk)
            print("candidate", candidate)
            print("candidate.pk", candidate.pk)
            print("candidate.person", candidate.person)
            print("candidate.person.pk", candidate.person.pk)
            print("booth", booth)
            print("booth.pk", booth.pk)
            print()

    @staticmethod
    def transfer(house_election, pref_objects, reader, row):
        current_round_numb = int(row[Command.ROUND_NUMBER_HEADER])
        if current_round_numb > 0:
            candidate, current_round, received, remaining, seat, transferred = \
                Command.fetch_transfer_data(current_round_numb, house_election,
                                            reader, row)
            if transferred > 0:
                Command.add_source(candidate, current_round, house_election,
                                   pref_objects, received, remaining, seat,
                                   transferred)

    @staticmethod
    def add_one_booth(house_election, row, bind=house.VoteTally):
        booth, seat = Command.set_booth_from_row(row)
        candidate, party, person = Command.fetch_candidate(
            house_election, row, seat)
        Command.set_ballot_position(candidate, house_election, party, person,
                                    row, seat)
        vote_tally, _ = bind.objects.get_or_create(
            booth=booth, election=house_election, candidate=candidate,
            primary_votes=int(row[Command.ORDINARY_VOTES_HEADER]))
        collection, _ = service.Collection.objects.get_or_create(
            booth=booth, election=house_election)

    @staticmethod
    def set_pref(house_election, pref_objects, reader, round_objects):
        row = next(reader)
        if row[Command.KIND_OF_VOTES_HEADER] == Command.PREFERENCE_VOTE_KIND:
            first_example, preference_attributes, seat = \
                Command.narrow_preferences(house_election, pref_objects,
                                           reader, round_objects, row)
            pref = Command.get_single_preference(first_example, pref_objects,
                                                 preference_attributes)
            Command.update_pref(house_election, pref, seat)

    @staticmethod
    def get_single_preference(first_example, pref_objects,
                              preference_attributes):
        if first_example:
            return first_example
        pref, _ = pref_objects.get_or_create(**preference_attributes)
        return pref

    @staticmethod
    def narrow_preferences(house_election, pref_objects, reader,
                           round_objects, row):
        candidate, pref_round, received, remaining, seat, transferred = \
            Command.fetch_pref_data(house_election, reader, round_objects, row)
        preference_attributes = {
            'candidate': candidate, 'election': house_election,
            'round': pref_round, 'seat': seat, 'votes_received': received,
            'votes_transferred': transferred, }
        return Command.remove_extras(pref_objects, preference_attributes), \
            preference_attributes, seat

    @staticmethod
    def set_all_preferences(house_election, pref_objects, reader,
                            round_objects):
        while True:
            try:
                Command.set_pref(house_election, pref_objects, reader,
                                 round_objects)
            except StopIteration:
                break

    @staticmethod
    def update_pref(house_election, pref, seat):
        if not pref.seat:
            pref.seat = seat
            pref.save()
        if not pref.election:
            pref.election = house_election
            pref.save()
