import os
from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models, csv_to_db, aec_codes
from ...constants import CANDIDATE_DIRECTORY_RELATIVE


class Command(BaseCommand, csv_to_db.ElectionReader):
    help = 'Add elections from csv files'

    def __call__(self, election_year, folder, type_of_date=datetime,
                 print_before_year="Election", quiet=False):
        Command.print_year(election_year, print_before_year, quiet)
        candidate_directory = os.path.join(folder,
                                           CANDIDATE_DIRECTORY_RELATIVE)
        senate_election, _ = models.SenateElection.objects.get_or_create(
            election_date=type_of_date(year=election_year, month=1, day=1))
        self.add_candidates(senate_election, candidate_directory)

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

    @staticmethod
    def add_one_candidate(election, row):
        candidate, person = Command.find_person(
            models.SenateCandidate.objects,
            Command.get_standard_person_attributes(row), row)
        selection, _ = models.Selection.objects.get_or_create(
            person=person,
            party=Command.fetch_party(row),
            election=election)