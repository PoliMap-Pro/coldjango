import csv
import os
from datetime import datetime
from operator import itemgetter
from django.core.management.base import BaseCommand
from ... import models

ELECTION_DIRECTORIES = {year: f".\\jacobsladder\\{year}\\" for year in
                        (2022, 2019, 2016, 2013, 2010, 2007, 2004)}
BOOTHS_DIRECTORY_RELATIVE = "prefs\\"
PREFERENCE_DISTRIBUTION_DIRECTORY_RELATIVE = "distribution_of_preferences\\"
SEATS_DIRECTORY_RELATIVE = "votes_counted\\"
TWO_CANDIDATE_PREFERRED_DIRECTORY_RELATIVE = "two_candidate_preferred\\"


class StringCode(str):
    # Column headers from the csv files
    CANDIDATE_CODE_HEADER = 'CandidateID'
    PARTY_ABBREVIATION_HEADER = 'PartyAb'
    PARTY_NAME_HEADER = 'PartyNm'
    STATE_ABBREVIATION_HEADER = 'StateAb'

    DEFAULT_FILE_EXTENSION_FOR_SOURCE_FILES = ".csv"

    def __new__(cls, parts, parts_dictionary):
        return str.__new__(cls, "".join([parts_dictionary[part] if isinstance(
            part, super) else str(part) for part in parts]))

    @staticmethod
    def walk(directory, file_extension=DEFAULT_FILE_EXTENSION_FOR_SOURCE_FILES):
        for base_path, directories, files in os.walk(directory):
            for file in files:
                if file.endswith(file_extension):
                    yield os.path.join(base_path, file)

    @staticmethod
    def get_last_known(house_election, row):
        return StringCode((StringCode.CANDIDATE_CODE_HEADER,
                           StringCode.PARTY_ABBREVIATION_HEADER,
                           house_election.election_date.year), row)

    @staticmethod
    def echo(quiet, text_to_print, blank_before=True):
        if not quiet:
            if blank_before:
                print()
            print(text_to_print)

class Command(BaseCommand):
    # Column headers from the csv files
    BALLOT_ORDER_HEADER = 'BallotPosition'
    BOOTH_CODE_HEADER = 'PollingPlaceID'
    BOOTH_NAME_HEADER = 'PollingPlace'
    ENROLLMENT_HEADER = 'Enrolment'
    FIRST_NAME_HEADER = 'Surname'
    KIND_OF_VOTES_HEADER = 'CalculationType'
    NUMBER_OF_VOTES_HEADER = 'CalculationValue'
    ORDINARY_VOTES_HEADER = 'OrdinaryVotes'
    OTHER_NAMES_HEADER = 'GivenNm'
    ROUND_NUMBER_HEADER = 'CountNumber'
    SEAT_CODE_HEADER = 'DivisionID'
    SEAT_NAME_HEADER = 'DivisionNm'

    PREFERENCE_VOTE_KIND = 'Preference Count'
    help = 'Add elections from csv files'



    def __call__(self, election_year, folder, pref_objects, round_objects):
        booths_directory, house_election, preference_distribution_directory, \
            seats_directory, two_candidate_preferred_directory = \
            self.start_election(election_year, folder)
        self.add_seats(house_election, seats_directory)
        self.add_booths(booths_directory, house_election)
        self.add_votes(house_election, two_candidate_preferred_directory)
        self.first_pass_preferences(house_election, pref_objects,
                                    preference_distribution_directory,
                                    round_objects)
        self.second_pass_preferences(house_election, pref_objects,
                                     preference_distribution_directory)

    def add_one(self, filename, house_election, single_create_method):
        with open(filename, "r") as in_file:
            reader = self.fetch_reader(filename, in_file)
            method = getattr(Command, single_create_method)
            [method(house_election, row) for row in reader]

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
                        row = next(reader)
                        if row[Command.KIND_OF_VOTES_HEADER] == \
                                Command.PREFERENCE_VOTE_KIND:
                            if int(row[Command.NUMBER_OF_VOTES_HEADER]) > 0:
                                Command.transfer(house_election, pref_objects,
                                                 reader, row)
                    except StopIteration:
                        StringCode.echo(quiet, "", False)
                        break

    def add_booths(self, booths_directory, house_election,
                   single_create_method='add_one_booth',
                   text_to_print="Reading files in booths directory",
                   quiet=False):
        StringCode.echo(quiet, text_to_print)
        [self.add_one(filename, house_election, single_create_method) for
         filename in StringCode.walk(booths_directory)]

    def add_votes(self, house_election, two_candidate_preferred_directory,
                  single_create_method='add_one_tally',
                  text_to_print="Reading files in two candidate preferred "
                                "directory", quiet=False):
        StringCode.echo(quiet, text_to_print)
        for filename in StringCode.walk(two_candidate_preferred_directory):
            self.add_one(filename, house_election, single_create_method)
            StringCode.echo(quiet, "", False)

    def add_seats(self, house_election, seats_directory,
                  single_create_method='add_one_seat',
                  text_to_print="Reading files in seats directory",
                  quiet=False):
        StringCode.echo(quiet, text_to_print, False)
        [self.add_one(filename, house_election, single_create_method) for
         filename in StringCode.walk(seats_directory)]

    def handle(self, *arguments, **keywordarguments):
        pref_objects = models.CandidatePreference.objects
        round_objects = models.PreferenceRound.objects
        election_items = list(ELECTION_DIRECTORIES.items())
        election_items.sort(key=itemgetter(0))
        election_items.reverse()
        [self(election_year, folder, pref_objects, round_objects) for
         election_year, folder in election_items]

    @staticmethod
    def fetch_transfer_data(current_round_numb, house_election, reader, row):
        candidate, received, seat = \
            Command.fetch_candid(house_election, row)
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
    def add_one_tally(house_election, row):
        candidate = models.HouseCandidate.objects.get(
            person=models.Person.objects.get(
                name=row[Command.FIRST_NAME_HEADER],
                other_names=row[Command.OTHER_NAMES_HEADER],
                last_known_codepartyyear=StringCode.get_last_known(
                    house_election, row)))
        vote_tally = models.VoteTally.objects.get(
            booth=models.Booth.objects.get(name=row[Command.BOOTH_NAME_HEADER],
                                           polling_place_aec_code=row[
                                               Command.BOOTH_CODE_HEADER]),
            election=house_election, candidate=candidate)
        vote_tally.tcp_votes = int(row[Command.ORDINARY_VOTES_HEADER])
        vote_tally.save()

    @staticmethod
    def add_source(candidate, current_round, house_election, pref_objects,
                   received, remaining, seat, transferred):
        preference_attributes = {
            'candidate': candidate,
            'election': house_election,
            'round': current_round,
            'votes_received': received,
            'votes_transferred': transferred,
        }
        #for gref in pref_objects.filter(votes_received=0,
        #                                            votes_transferred__lt=0,
        #                                           round=current_round,
        #                                             election=house_election,
        #                                             seat=seat):
            #print(gref)
            #print("___________________________________")
            #print(gref, gref.pk)
            #print(gref.votes_received)
            #print(gref.votes_transferred)
            #print(gref.round)
            #print(gref.election)
            #print(gref.seat)
            #print(gref.candidate)
        try:
            pref = pref_objects.get(**preference_attributes)
            pref.source_candidate = pref_objects.get(votes_received=0,
                                                     votes_transferred__lt=0,
                                                     round=current_round,
                                                     election=house_election,
                                                     seat=seat).candidate
            pref.save()
        except models.CandidatePreference.MultipleObjectsReturned:
            assert all([pref.source_candidate for pref in
                        pref_objects.filter(**preference_attributes)])

    @staticmethod
    def fetch_pref_data(house_election, reader, round_objects, row):
        candidate, received, seat = Command.fetch_candid(house_election, row)
        transferred = Command.advance(reader)
        round_obj, _ = round_objects.get_or_create(
            seat=seat, election=house_election,
            round_number=int(row[Command.ROUND_NUMBER_HEADER]))
        return candidate, round_obj, received, received, seat, transferred

    @staticmethod
    def fetch_reader(filename, in_file, type_of_reader=csv.DictReader,
                     quiet=False):
        StringCode.echo(quiet, filename, False)
        next(in_file)
        return type_of_reader(in_file)

    @staticmethod
    def add_one_seat(house_election, row):
        seat, _ = models.Seat.objects.get_or_create(
            name=row[Command.SEAT_NAME_HEADER],
            state=row[StringCode.STATE_ABBREVIATION_HEADER].lower(),
            division_aec_code=row[Command.SEAT_CODE_HEADER])
        seat.elections.add(house_election)
        enrollment, _ = models.Enrollment.objects.get_or_create(
            seat=seat, election=house_election,
            number_enrolled=int(row[Command.ENROLLMENT_HEADER]))

    @staticmethod
    def fetch_candidate(house_election, row, type_of_code=StringCode):
        person, _ = models.Person.objects.get_or_create(
            name=row[Command.FIRST_NAME_HEADER],
            other_names=row[Command.OTHER_NAMES_HEADER],
            last_known_codepartyyear=type_of_code.get_last_known(house_election,
                                                                 row))
        candidate, _ = models.HouseCandidate.objects.get_or_create(
            person=person)
        party, _ = models.Party.objects.get_or_create(
            name=row[StringCode.PARTY_NAME_HEADER], abbreviation=row[
                StringCode.PARTY_ABBREVIATION_HEADER])
        return candidate, party, person

    @staticmethod
    def set_booths(house_election, row):
        booth, _ = models.Booth.objects.get_or_create(
            name=row[Command.BOOTH_NAME_HEADER],
            polling_place_aec_code=row[Command.BOOTH_CODE_HEADER])
        seat = models.Seat.objects.get(name=row[Command.SEAT_NAME_HEADER],
                                       division_aec_code=row[
                                           Command.SEAT_CODE_HEADER])
        collection, _ = models.Collection.objects.get_or_create(
            booth=booth, seat=seat, election=house_election)
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
    def add_one_booth(house_election, row):
        booth, seat = Command.set_booths(house_election, row)
        candidate, party, person = Command.fetch_candidate(house_election, row)
        Command.add_tally(booth, candidate, house_election, party, person, row,
                          seat)

    @staticmethod
    def set_pref(house_election, pref_objects, reader, round_objects):
        row = next(reader)
        if row[Command.KIND_OF_VOTES_HEADER] == Command.PREFERENCE_VOTE_KIND:
            candidate, pref_round, received, remaining, seat, \
                transferred = Command.fetch_pref_data(
                    house_election, reader, round_objects, row)
            preference_attributes = {
                'candidate': candidate,
                'election': house_election,
                'round': pref_round,
                'seat': seat,
                'votes_received': received,
                'votes_transferred': transferred,}
            first_example = Command.remove_extras(pref_objects,
                                                  preference_attributes)
            if first_example:
                pref = first_example
            else:
                pref, _ = pref_objects.get_or_create(**preference_attributes)
            Command.update_pref(house_election, pref, seat)

    @staticmethod
    def remove_extras(model_objects, attribute_dict):
        if model_objects.filter(**attribute_dict).count() > 1:
            modls = model_objects.filter(**attribute_dict)
            [extra.delete() for extra in modls[1:]]
            return modls[0]
        return False

    @staticmethod
    def add_tally(booth, candidate, house_election, party, person, row, seat):
        representation, _ = models.Representation.objects.get_or_create(
            person=person, party=party, election=house_election)
        contention, _ = models.Contention.objects.get_or_create(
            seat=seat, candidate=candidate,
            candidate_aec_code=row[StringCode.CANDIDATE_CODE_HEADER],
            election=house_election,
            ballot_position=row[Command.BALLOT_ORDER_HEADER])
        vote_tally, _ = models.VoteTally.objects.get_or_create(
            booth=booth, election=house_election,
            candidate=candidate,
            primary_votes=int(row[Command.ORDINARY_VOTES_HEADER]))

    @staticmethod
    def fetch_candid(house_election, row, type_of_code=StringCode):
        """
        Fetch the person, then use it to fetch the candidate
        """

        return models.HouseCandidate.objects.get(
            person=models.Person.objects.get(name=row[
                Command.FIRST_NAME_HEADER],
                                             other_names=row[Command.OTHER_NAMES_HEADER],
                                             last_known_codepartyyear=type_of_code.get_last_known(
                                                 house_election, row))), \
            int(row[Command.NUMBER_OF_VOTES_HEADER]), \
            models.Seat.objects.get(name=row[Command.SEAT_NAME_HEADER],
                                    division_aec_code=row[
                                        Command.SEAT_CODE_HEADER])

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
        if not quiet:
            print(print_before_year, election_year)
            print()
        house_election, _ = models.HouseElection.objects.get_or_create(
            election_date=type_of_date(year=election_year, month=1, day=1))
        return os.path.join(folder, BOOTHS_DIRECTORY_RELATIVE), \
            house_election, os.path.join(
            folder, PREFERENCE_DISTRIBUTION_DIRECTORY_RELATIVE), \
            os.path.join(folder, SEATS_DIRECTORY_RELATIVE), \
            os.path.join(folder, TWO_CANDIDATE_PREFERRED_DIRECTORY_RELATIVE)
