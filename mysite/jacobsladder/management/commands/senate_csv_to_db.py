import os
from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models, csv_to_db, aec_codes
from ...constants import CANDIDATE_DIRECTORY_RELATIVE, \
    LIGHTHOUSES_DIRECTORY_RELATIVE


class Command(BaseCommand, csv_to_db.ElectionReader):
    RELATIVE_DIRECTORIES = (CANDIDATE_DIRECTORY_RELATIVE,
                            LIGHTHOUSES_DIRECTORY_RELATIVE)

    help = 'Add elections from csv files'

    def __call__(self, election_year, folder, type_of_date=datetime,
                 print_before_year="Election", quiet=False):
        Command.print_year(election_year, print_before_year, quiet)
        candidate_directory, lighthouses_directory = [
            os.path.join(folder, relative_directory) for relative_directory in
            Command.RELATIVE_DIRECTORIES]
        senate_election, _ = models.SenateElection.objects.get_or_create(
            election_date=type_of_date(year=election_year, month=1, day=1))
        self.add_candidates(senate_election, candidate_directory)
        self.add_lighthouses(senate_election, lighthouses_directory)

    def handle(self, *arguments, **keywordarguments):
        election_items = Command.get_election_items()
        [self(election_year, folder) for election_year, folder in
         election_items]

    def add_candidates(self, election, directory,
                       single_create_method='add_one_candidate',
                       text_to_print="Reading files in candidates directory",
                       quiet=False):
        self.map_report_with_blank_line(directory, election, quiet,
                                        single_create_method, text_to_print)

    def add_lighthouses(self, election, directory,
                        single_create_method='add_one_lighthouse',
                        text_to_print="Reading files in lighthouses directory",
                        quiet=False):
        self.map_report_with_blank_line(directory, election, quiet,
                                        single_create_method, text_to_print)

    @staticmethod
    def add_one_candidate(election, row):
        candidate, person = Command.find_person(
            models.SenateCandidate.objects,
            Command.get_standard_person_attributes(row), row)
        selection, _ = models.Selection.objects.get_or_create(
            person=person,
            party=Command.fetch_party(row),
            election=election)

    @staticmethod
    def add_one_lighthouse(election, row):
        lighthouse, _ = models.Lighthouse.objects.get_or_create(
            name=row[Command.SEAT_NAME_HEADER])
        lighthouse.elections.add(election)
        lighthouse.state = row[
            aec_codes.StringCode.STATE_ABBREVIATION_HEADER].lower()
        lighthouse.save()
        lighthouse_code, _ = models.LighthouseCode.objects.get_or_create(
            lighthouse=lighthouse, number=int(row[Command.SEAT_CODE_HEADER]))
