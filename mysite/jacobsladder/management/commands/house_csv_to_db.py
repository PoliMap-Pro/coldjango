import os
from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models, csv_to_db
from ...constants import BOOTHS_DIRECTORY_RELATIVE, \
    HOUSE_DISTRIBUTION_DIRECTORY_RELATIVE, SEATS_DIRECTORY_RELATIVE, \
    TWO_CANDIDATE_PREFERRED_DIRECTORY_RELATIVE
from ...aec_codes import StringCode


class Command(BaseCommand, csv_to_db.ElectionReader):
    PREFERENCE_VOTE_KIND = 'Preference Count'
    help = 'Add elections from csv files'

    def __call__(self, election_year, folder, pref_objects, round_objects):
        booths_directory, house_election, preference_distribution_directory, \
            seats_directory, two_candidate_preferred_directory = \
            self.start_election(election_year, folder)
        self.setup(booths_directory, house_election, seats_directory,
                   two_candidate_preferred_directory)
        self.first_pass_preferences(house_election, pref_objects,
                                    preference_distribution_directory,
                                    round_objects)
        self.second_pass_preferences(house_election, pref_objects,
                                     preference_distribution_directory)

    def setup(self, booths_directory, house_election, seats_directory,
              two_candidate_preferred_directory):
        self.add_seats(house_election, seats_directory)
        self.add_booths(booths_directory, house_election)
        self.add_votes(house_election, two_candidate_preferred_directory)

    def first_pass_preferences(self, house_election, pref_objects,
                               preference_distribution_directory,
                               round_objects,
                               text_to_print="First Pass: Reading files in "
                                             "preference distribution "
                                             "directory", quiet=False):
        StringCode.echo(quiet, text_to_print, False)
        for filename in StringCode.walk(preference_distribution_directory):
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
        StringCode.echo(quiet, text_to_print)
        for filename in StringCode.walk(preference_distribution_directory):
            with open(filename, "r") as in_file:
                reader = self.fetch_reader(filename, in_file)
                while True:
                    try:
                        Command.transfer_if_preference(house_election,
                                                       pref_objects, reader)
                    except StopIteration:
                        StringCode.echo(quiet, "", False)
                        break

    def add_booths(self, directory, election,
                   single_create_method='add_one_booth',
                   text_to_print="Reading files in booths directory",
                   quiet=False):
        self.map_report_with_blank_line(directory, election, quiet,
                                        single_create_method, text_to_print)

    def add_votes(self, election, directory,
                  single_create_method='add_one_tally',
                  text_to_print="Reading files in two candidate preferred "
                                "directory", quiet=False):
        StringCode.echo(quiet, text_to_print)
        for filename in StringCode.walk(directory):
            self.add_one(filename, election, single_create_method)
            StringCode.echo(quiet, "", False)

    def add_seats(self, election, directory,
                  single_create_method='add_one_seat',
                  text_to_print="Reading files in seats directory",
                  quiet=False):
        self.map_report_without_blank_line(directory, election, quiet,
                                           single_create_method, text_to_print)

    def handle(self, *arguments, **keywordarguments):
        pref_objects = models.CandidatePreference.objects
        round_objects = models.PreferenceRound.objects
        election_items = Command.get_election_items()
        [self(election_year, folder, pref_objects, round_objects) for
         election_year, folder in election_items]

    @staticmethod
    def fetch_candid(house_election, row):
        """
        Fetch the person, then use it to fetch the candidate
        """

        candidate, seat = Command.find_candidate_for_seat(house_election, row)
        return candidate, int(row[Command.NUMBER_OF_VOTES_HEADER]), seat

    @staticmethod
    def fetch_transfer_data(current_round_numb, house_election, reader, row):
        candidate, received, seat = Command.fetch_candid(house_election, row)
        transferred = Command.advance(reader)
        return candidate, models.PreferenceRound.objects.get(
            seat=seat, election=house_election,
            round_number=current_round_numb), received, received, seat, \
            transferred

    @staticmethod
    def advance(reader):
        next(reader)
        return int(next(reader)[Command.NUMBER_OF_VOTES_HEADER])

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
            booth_attributes, models.Booth.objects, models.BoothCode.objects,
            'booth', int(row[Command.BOOTH_CODE_HEADER]))
        try:
            Command.get_two_candidate_pref_votes(booth, candidate,
                                                 house_election, row)
        except models.VoteTally.DoesNotExist:
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
    def get_two_candidate_pref_votes(booth, candidate, house_election, row):
        vote_tally = models.VoteTally.objects.get(booth=booth,
                                                  election=house_election,
                                                  candidate=candidate)
        vote_tally.tcp_votes = int(row[Command.ORDINARY_VOTES_HEADER])
        vote_tally.save()

    @staticmethod
    def find_candidate_for_seat(house_election, row):
        seat = Command.fetch_by_aec_code(
            Command.get_standard_beacon_attributes(row), models.Seat.objects,
            models.SeatCode.objects, 'seat',
            int(row[Command.SEAT_CODE_HEADER]))
        candidate = Command.pull_candidate(
            house_election, Command.get_standard_person_attributes(row), row,
            seat)
        return candidate, seat

    @staticmethod
    def pull_candidate(election, person_attributes, row, seat,
                       candidate_objects=models.HouseCandidate.objects):
        candidate, _ = Command.find_person(candidate_objects,
                                           person_attributes, row)
        contention, _ = models.Contention.objects.get_or_create(
            seat=seat, candidate=candidate, election=election)
        return candidate

    @staticmethod
    def add_source(candidate, current_round, house_election, pref_objects,
                   received, remaining, seat, transferred):
        preference_attributes = {'candidate': candidate,
                                 'election': house_election,
                                 'round': current_round,
                                 'votes_received': received,
                                 'votes_transferred': transferred,}
        try:
            Command.single_preference(current_round, house_election,
                                      pref_objects, preference_attributes, seat)
        except models.CandidatePreference.MultipleObjectsReturned:
            assert all([pref.source_candidate for pref in
                        pref_objects.filter(**preference_attributes)])

    @staticmethod
    def single_preference(current_round, house_election, pref_objects,
                          preference_attributes, seat):
        pref = pref_objects.get(**preference_attributes)
        pref.source_candidate = pref_objects.get(votes_received=0,
                                                 votes_transferred__lt=0,
                                                 round=current_round,
                                                 election=house_election,
                                                 seat=seat).candidate
        pref.save()

    @staticmethod
    def fetch_pref_data(house_election, reader, round_objects, row):
        candidate, received, seat = Command.fetch_candid(house_election, row)
        transferred = Command.advance(reader)
        round_obj, _ = round_objects.get_or_create(
            seat=seat, election=house_election,
            round_number=int(row[Command.ROUND_NUMBER_HEADER]))
        return candidate, round_obj, received, received, seat, transferred

    @staticmethod
    def add_one_seat(election, row, code_objects=models.SeatCode.objects):
        seat = Command.find_seat(election, row)
        seat_code, _ = code_objects.get_or_create(
            seat=seat, number=int(row[Command.SEAT_CODE_HEADER]))
        enrollment, _ = models.Enrollment.objects.get_or_create(
            seat=seat, election=election, number_enrolled=int(
                row[Command.ENROLLMENT_HEADER]))

    @staticmethod
    def find_seat(house_election, row, beacon_objects=models.Seat.objects):
        seat = Command.set_seat_election(beacon_objects, house_election, row)
        seat.state = row[StringCode.STATE_ABBREVIATION_HEADER].lower()
        seat.save()
        return seat

    @staticmethod
    def fetch_candidate(house_election, row, seat, tag=models.Party):
        candidate = Command.pull_candidate(
            house_election, Command.get_standard_person_attributes(row), row,
            seat)
        party, _ = tag.objects.get_or_create(name=row[
            StringCode.PARTY_NAME_HEADER], abbreviation=row[
            StringCode.PARTY_ABBREVIATION_HEADER])
        return candidate, party, candidate.person

    @staticmethod
    def set_booth_from_row(row, code_objects=models.SeatCode.objects):
        seat = Command.fetch_by_aec_code(
            Command.get_standard_beacon_attributes(row), models.Seat.objects,
            code_objects, 'seat', int(row[Command.SEAT_CODE_HEADER]))
        booth, _ = models.Booth.objects.get_or_create(
            name=row[Command.BOOTH_NAME_HEADER], seat=seat)
        booth_code, _ = models.BoothCode.objects.get_or_create(
            booth=booth, number=int(row[Command.BOOTH_CODE_HEADER]))
        return booth, seat

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
    def add_one_booth(house_election, row, bind=models.VoteTally):
        booth, seat = Command.set_booth_from_row(row)
        candidate, party, person = Command.fetch_candidate(
            house_election, row, seat)
        Command.set_ballot_position(candidate, house_election, party, person,
                                    row, seat)
        vote_tally, _ = bind.objects.get_or_create(
            booth=booth, election=house_election, candidate=candidate,
            primary_votes=int(row[Command.ORDINARY_VOTES_HEADER]))

    @staticmethod
    def set_ballot_position(candidate, house_election, party, person, row,
                            seat):
        representation, _ = models.Representation.objects.get_or_create(
            person=person, party=party, election=house_election)
        contention, _ = models.Contention.objects.get_or_create(
            seat=seat, candidate=candidate, election=house_election)
        contention.ballot_position = row[Command.BALLOT_ORDER_HEADER]
        contention.save()

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
    def remove_extras(model_objects, attribute_dict):
        if model_objects.filter(**attribute_dict).count() > 1:
            modls = model_objects.filter(**attribute_dict)
            [extra.delete() for extra in modls[1:]]
            return modls[0]
        return False

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

    @staticmethod
    def start_election(election_year, folder, type_of_date=datetime,
                       print_before_year="Election", quiet=False):
        Command.print_year(election_year, print_before_year, quiet)
        house_election, _ = models.HouseElection.objects.get_or_create(
            election_date=type_of_date(year=election_year, month=1, day=1))
        return os.path.join(folder, BOOTHS_DIRECTORY_RELATIVE), \
            house_election, os.path.join(
            folder, HOUSE_DISTRIBUTION_DIRECTORY_RELATIVE), \
            os.path.join(folder, SEATS_DIRECTORY_RELATIVE), \
            os.path.join(folder, TWO_CANDIDATE_PREFERRED_DIRECTORY_RELATIVE)
