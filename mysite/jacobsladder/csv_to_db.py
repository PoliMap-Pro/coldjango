import csv
from operator import itemgetter

from . import models, aec_codes
from .aec_codes import StringCode
from .constants import ELECTION_DIRECTORIES
#from .management.commands.house_csv_to_db import Command


class AECCodeReader(object):
    BALLOT_ORDER_HEADER = 'BallotPosition'
    KIND_OF_VOTES_HEADER = 'CalculationType'
    NUMBER_OF_VOTES_HEADER = 'CalculationValue'
    ORDINARY_VOTES_HEADER = 'OrdinaryVotes'

    def add_one(self, filename, election, single_create_method):
        with open(filename, "r") as in_file:
            reader = self.fetch_reader(filename, in_file)
            method = getattr(self.__class__, single_create_method)
            [method(election, row) for row in reader]

    def map_report(self, directory, election, quiet, single_create_method,
                   text_to_print, blank_line):
        aec_codes.StringCode.echo(quiet, text_to_print, blank_line)
        [self.add_one(filename, election, single_create_method) for filename
         in aec_codes.StringCode.walk(directory)]

    @staticmethod
    def fetch_reader(filename, in_file, type_of_reader=csv.DictReader,
                     quiet=False):
        aec_codes.StringCode.echo(quiet, filename, False)
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
    def print_year(election_year, print_before_year, quiet):
        if not quiet:
            print(print_before_year, election_year)
            print()


class ElectionReader(AECCodeReader):
    BOOTH_NAME_HEADER = 'PollingPlace'
    BOOTH_CODE_HEADER = 'PollingPlaceID'
    ENROLLMENT_HEADER = 'Enrolment'
    FIRST_NAME_HEADER = 'Surname'
    OTHER_NAMES_HEADER = 'GivenNm'
    ROUND_NUMBER_HEADER = 'CountNumber'
    SEAT_CODE_HEADER = 'DivisionID'
    SEAT_NAME_HEADER = 'DivisionNm'

    def map_report_with_blank_line(self, directory, election, quiet,
                                   single_create_method, text_to_print):
        self.map_report(directory, election, quiet, single_create_method,
                        text_to_print, True)

    def map_report_without_blank_line(self, directory, election, quiet,
                                      single_create_method, text_to_print):
        self.map_report(directory, election, quiet, single_create_method,
                        text_to_print, False)

    @classmethod
    def find_person(cls, candidate_objects, person_attributes, row):
        person = cls.fetch_by_aec_code(
            person_attributes, models.Person.objects, models.PersonCode.objects,
            'person', int(row[aec_codes.StringCode.CANDIDATE_CODE_HEADER]))
        candidate, _ = candidate_objects.get_or_create(person=person)
        return candidate, person

    @staticmethod
    def get_election_items():
        election_items = list(ELECTION_DIRECTORIES.items())
        election_items.sort(key=itemgetter(0))
        election_items.reverse()
        return election_items

    @staticmethod
    def get_standard_person_attributes(row):
        return {'name': row[ElectionReader.FIRST_NAME_HEADER],
                'other_names': row[ElectionReader.OTHER_NAMES_HEADER], }

    @staticmethod
    def fetch_party(row):
        party_name = row[StringCode.PARTY_NAME_HEADER]
        if party_name:
            party_abbreviation = row[StringCode.PARTY_ABBREVIATION_HEADER]
            if party_abbreviation:
                party, _ = models.Party.objects.get_or_create(
                    name=party_name, abbreviation=party_abbreviation)
                return party
        return None

    @staticmethod
    def get_standard_beacon_attributes(row):
        return {'name': row[ElectionReader.SEAT_NAME_HEADER],
                'state': row[StringCode.STATE_ABBREVIATION_HEADER].lower(), }
