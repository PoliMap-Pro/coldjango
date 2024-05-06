import os
from datetime import datetime

from . import models
from .constants import BOOTHS_DIRECTORY_RELATIVE, HOUSE_DISTRIBUTION_DIRECTORY_RELATIVE, SEATS_DIRECTORY_RELATIVE, \
    TWO_CANDIDATE_PREFERRED_DIRECTORY_RELATIVE
from .management.commands.house_csv_to_db import Command

from ..jacobsladder import csv_to_db


class BaseCode(csv_to_db.ElectionReader):
    def setup(self, booths_directory, house_election, seats_directory,
              two_candidate_preferred_directory):
        self.add_seats(house_election, seats_directory)
        self.add_booths(booths_directory, house_election)
        self.add_votes(house_election, two_candidate_preferred_directory)

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
    def set_ballot_position(candidate, house_election, party, person, row,
                            seat):
        representation, _ = models.Representation.objects.get_or_create(
            person=person, party=party, election=house_election)
        contention, _ = models.Contention.objects.get_or_create(
            seat=seat, candidate=candidate, election=house_election)
        contention.ballot_position = row[Command.BALLOT_ORDER_HEADER]
        contention.save()

    @staticmethod
    def remove_extras(model_objects, attribute_dict):
        if model_objects.filter(**attribute_dict).count() > 1:
            modls = model_objects.filter(**attribute_dict)
            [extra.delete() for extra in modls[1:]]
            return modls[0]
        return False

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


class StringCode(str, BaseCode):
    # Column headers from the csv files
    CANDIDATE_CODE_HEADER = 'CandidateID'
    PARTY_ABBREVIATION_HEADER = 'PartyAb'
    PARTY_NAME_HEADER = 'PartyNm'
    STATE_ABBREVIATION_HEADER = 'StateAb'

    DEFAULT_DELIMITER = "-"
    DEFAULT_FILE_EXTENSION_FOR_SOURCE_FILES = ".csv"

    def __new__(cls, parts, parts_dictionary, delimiter=DEFAULT_DELIMITER):
        return str.__new__(cls, delimiter.join([parts_dictionary[part]
                                                if isinstance(
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