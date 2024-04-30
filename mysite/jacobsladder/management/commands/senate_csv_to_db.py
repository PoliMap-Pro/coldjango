import os
from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models, csv_to_db, aec_codes
from ...constants import CANDIDATE_DIRECTORY_RELATIVE, \
    LIGHTHOUSES_DIRECTORY_RELATIVE, FLOORS_DIRECTORY_RELATIVE


class Command(BaseCommand, csv_to_db.ElectionReader):
    RELATIVE_DIRECTORIES = (CANDIDATE_DIRECTORY_RELATIVE,
                            LIGHTHOUSES_DIRECTORY_RELATIVE,
                            FLOORS_DIRECTORY_RELATIVE, )
    FLOOR_NAME_HEADER = 'PollingPlaceNm'

    help = 'Add elections from csv files'

    def __call__(self, election_year, folder, type_of_date=datetime,
                 print_before_year="Election", quiet=False):
        Command.print_year(election_year, print_before_year, quiet)
        candidate_directory, lighthouses_directory, floors_directory = [
            os.path.join(folder, relative_directory) for relative_directory in
            Command.RELATIVE_DIRECTORIES]
        senate_election, _ = models.SenateElection.objects.get_or_create(
            election_date=type_of_date(year=election_year, month=1, day=1))
        self.add_candidates(senate_election, candidate_directory)
        self.add_lighthouses(senate_election, lighthouses_directory)
        self.add_floors(senate_election, floors_directory)

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

    def add_floors(self, election, directory,
                   single_create_method='add_one_floor',
                   text_to_print="Reading files in floors directory",
                   quiet=False):
        self.map_report_with_blank_line(directory, election, quiet,
                                        single_create_method, text_to_print)

    @staticmethod
    def add_one_candidate(election, row):
        candidate, person = Command.find_person(
            models.SenateCandidate.objects,
            Command.get_standard_person_attributes(row), row)
        selection, _ = models.Selection.objects.get_or_create(
            person=person, party=Command.fetch_party(row), election=election)

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

    @staticmethod
    def add_one_floor(election, row):
        lighthouse = Command.fetch_by_aec_code(
            Command.get_standard_beacon_attributes(row),
            models.Lighthouse.objects,
            models.LighthouseCode.objects, 'lighthouse',
            int(row[Command.SEAT_CODE_HEADER]))
        floor, _ = models.Floor.objects.get_or_create(
            name=row[Command.FLOOR_NAME_HEADER], lighthouse=lighthouse)
        floor_code, _ = models.FloorCode.objects.get_or_create(
            floor=floor, number=int(row[Command.BOOTH_CODE_HEADER]))
        name_parts = row['CandidateDetails'].split(", ", 1)
        person_attributes = {'name': name_parts[0], 'other_names': "" if len(
            name_parts) == 1 else name_parts[1], }
        candidate, _ = Command.find_person(models.SenateCandidate.objects,
                                           person_attributes, row)
        stand, _ = models.Stand.objects.get_or_create(candidate=candidate,
                                                      election=election)
        stand.ballot_position = int(row[Command.BALLOT_ORDER_HEADER])
        stand.save()
        group, _ = models.SenateGroup.objects.get_or_create(abbreviation=row[
            'Group'], election=election)
        candidate.group = group
        candidate.save()
        '''
        vote_tally, _ = models.VoteTally.objects.get_or_create(
            booth=booth, election=election,
            candidate=candidate,
            primary_votes=int(row[Command.ORDINARY_VOTES_HEADER]))
        '''