import csv
from operator import itemgetter
from . import models, aec_codes
from .aec_codes import StringCode
from .constants import ELECTION_DIRECTORIES


class AECReader(object):
    SEAT_NAME_HEADER = 'DivisionNm'
    FIRST_NAME_HEADER = 'Surname'
    OTHER_NAMES_HEADER = 'GivenNm'
    SEAT_CODE_HEADER = 'DivisionID'

    def add_one(self, filename, election, single_create_method,
                line_before_headers=True):
        with open(filename, "r") as in_file:
            reader = self.fetch_reader(filename, in_file,
                                       line_before_headers=line_before_headers)
            method = getattr(self.__class__, single_create_method)
            [method(election, row) for row in reader]

    @staticmethod
    def fetch_reader(filename, in_file, type_of_reader=csv.DictReader,
                     quiet=False, line_before_headers=True):
        aec_codes.StringCode.echo(quiet, filename, False)
        if line_before_headers:
            next(in_file)
        return type_of_reader(in_file)

    @staticmethod
    def fetch_by_aec_code(model_attributes, model_objects, code_objects,
                          related_name, target):
        if model_objects.filter(**model_attributes).count() > 1:
            code_attributes = {'__'.join([related_name, key]): value for
                               key, value in model_attributes.items()}
            codes = [code for code in code_objects.filter(
                **code_attributes) if code.number == target]
            print("\t-filtered by code:", codes[0], codes[0].pk, related_name)
            return getattr(codes[0], related_name)
        try:
            return model_objects.get(**model_attributes)
        except Exception:
            new_model = model_objects.create(**model_attributes)
            new_attributes = {'number': target, related_name: new_model}
            new_code = code_objects.create(**new_attributes)
            return new_model

    @staticmethod
    def get_standard_beacon_attributes(row):
        return {'name': row[ElectionReader.SEAT_NAME_HEADER],
                'state': row[StringCode.STATE_ABBREVIATION_HEADER].lower(), }

    @classmethod
    def find_person(cls, candidate_objects, person_attributes, row):
        try:
            person = cls.fetch_by_aec_code(
                person_attributes, models.Person.objects,
                models.PersonCode.objects, 'person', int(
                    row[aec_codes.StringCode.CANDIDATE_CODE_HEADER]))
        except KeyError:
            person, _ = models.Person.objects.get_or_create(**person_attributes)
        candidate, _ = candidate_objects.get_or_create(person=person)
        return candidate, person

    @staticmethod
    def get_standard_person_attributes(row):
        return {'name': row[ElectionReader.FIRST_NAME_HEADER],
                'other_names': row[ElectionReader.OTHER_NAMES_HEADER], }

    @staticmethod
    def find_candidate_for_seat(house_election, row):
        seat = AECReader.fetch_by_aec_code(
            AECReader.get_standard_beacon_attributes(row), models.Seat.objects,
            models.SeatCode.objects, 'seat', int(row[Command.SEAT_CODE_HEADER]))
        candidate = AECReader.pull_candidate(
            house_election, AECReader.get_standard_person_attributes(row), row,
            seat)
        return candidate, seat

    @staticmethod
    def pull_candidate(election, person_attributes, row, seat,
                       candidate_objects=models.HouseCandidate.objects):
        candidate, _ = AECReader.find_person(candidate_objects,
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


class AECCodeReader(AECReader):
    ALTERNATIVE_BALLOT_ORDER_HEADER = 'Ballot Position'
    BALLOT_ORDER_HEADER = 'BallotPosition'
    KIND_OF_VOTES_HEADER = 'CalculationType'
    NUMBER_OF_VOTES_HEADER = 'CalculationValue'
    ORDINARY_VOTES_HEADER = 'OrdinaryVotes'

    def map_report(self, directory, election, quiet, single_create_method,
                   text_to_print, blank_line, line_before_headers=True):
        aec_codes.StringCode.echo(quiet, text_to_print, blank_line)
        [self.add_one(filename, election, single_create_method,
                      line_before_headers) for filename in
         aec_codes.StringCode.walk(directory)]

    @staticmethod
    def print_year(election_year, print_before_year, quiet):
        if not quiet:
            print(print_before_year, election_year)
            print()

    @staticmethod
    def set_seat_election(beacon_objects, house_election, row):
        seat, _ = beacon_objects.get_or_create(name=row[
            ElectionReader.SEAT_NAME_HEADER])
        seat.elections.add(house_election)
        return seat

    @staticmethod
    def fetch_candid(house_election, row):
        """
        Fetch the person, then use it to fetch the candidate
        """

        candidate, seat = AECCodeReader.find_candidate_for_seat(house_election,
                                                                row)
        return candidate, int(row[AECCodeReader.NUMBER_OF_VOTES_HEADER]), seat

    @staticmethod
    def advance(reader):
        next(reader)
        return int(next(reader)[AECCodeReader.NUMBER_OF_VOTES_HEADER])

    @staticmethod
    def get_two_candidate_pref_votes(booth, candidate, house_election, row):
        vote_tally = models.VoteTally.objects.get(booth=booth,
                                                  election=house_election,
                                                  candidate=candidate)
        vote_tally.tcp_votes = int(row[AECCodeReader.ORDINARY_VOTES_HEADER])
        vote_tally.save()


class ElectionReader(AECCodeReader):
    BOOTH_NAME_HEADER = 'PollingPlace'
    BOOTH_CODE_HEADER = 'PollingPlaceID'
    ENROLLMENT_HEADER = 'Enrolment'
    ROUND_NUMBER_HEADER = 'CountNumber'

    def map_report_with_blank_line(self, directory, election, quiet,
                                   single_create_method, text_to_print,
                                   line_before_headers=True):
        self.map_report(directory, election, quiet, single_create_method,
                        text_to_print, True, line_before_headers)

    def map_report_without_blank_line(self, directory, election, quiet,
                                      single_create_method, text_to_print,
                                      line_before_headers=True):
        self.map_report(directory, election, quiet, single_create_method,
                        text_to_print, False, line_before_headers)

    @staticmethod
    def get_election_items(sort_key=itemgetter(0)):
        election_items = list(ELECTION_DIRECTORIES.items())
        election_items.sort(key=sort_key)
        election_items.reverse()
        return election_items

    @staticmethod
    def fetch_party(row, bind=models.Party):
        party_name = row[StringCode.PARTY_NAME_HEADER]
        if party_name:
            party_abbreviation = row[StringCode.PARTY_ABBREVIATION_HEADER]
            if party_abbreviation:
                party, _ = bind.objects.get_or_create(
                    name=party_name, abbreviation=party_abbreviation)
                return party
        return None

    @staticmethod
    def fetch_pref_data(house_election, reader, round_objects, row):
        candidate, received, seat = ElectionReader.fetch_candid(house_election,
                                                                row)
        transferred = ElectionReader.advance(reader)
        round_obj, _ = round_objects.get_or_create(
            seat=seat, election=house_election,
            round_number=int(row[ElectionReader.ROUND_NUMBER_HEADER]))
        return candidate, round_obj, received, received, seat, transferred

    @staticmethod
    def find_seat(house_election, row, beacon_objects=models.Seat.objects):
        seat = ElectionReader.set_seat_election(beacon_objects, house_election,
                                                row)
        seat.state = row[StringCode.STATE_ABBREVIATION_HEADER].lower()
        seat.save()
        return seat

    @staticmethod
    def add_one_seat(election, row, code_objects=models.SeatCode.objects):
        seat = ElectionReader.find_seat(election, row)
        seat_code, _ = code_objects.get_or_create(
            seat=seat, number=int(row[ElectionReader.SEAT_CODE_HEADER]))
        enrollment, _ = models.Enrollment.objects.get_or_create(
            seat=seat, election=election, number_enrolled=int(
                row[ElectionReader.ENROLLMENT_HEADER]))
