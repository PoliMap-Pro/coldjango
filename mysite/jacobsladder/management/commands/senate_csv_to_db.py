import os
from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models, csv_to_db, aec_codes
from ...constants import CANDIDATE_DIRECTORY_RELATIVE, \
    LIGHTHOUSES_DIRECTORY_RELATIVE, FLOORS_DIRECTORY_RELATIVE, \
    SENATE_DISTRIBUTION_DIRECTORY_RELATIVE


class Command(BaseCommand, csv_to_db.ElectionReader):
    RELATIVE_DIRECTORIES = (CANDIDATE_DIRECTORY_RELATIVE,
                            LIGHTHOUSES_DIRECTORY_RELATIVE,
                            FLOORS_DIRECTORY_RELATIVE,
                            SENATE_DISTRIBUTION_DIRECTORY_RELATIVE)
    MAPS = (('add_one_candidate', "Reading files in candidates directory"),
            ('add_one_lighthouse', "Reading files in lighthouses directory"),
            ('add_one_floor', "Reading files in floors directory"),
            ('add_one_preference',
             "First pass: reading files in preferences directory"),
            ('add_one_source',
             "Second pass: reading files in preferences directory"))
    FLOOR_NAME_HEADER = 'PollingPlaceNm'
    ALTERNATIVE_GROUP_HEADER = 'Ticket'

    help = 'Add elections from csv files'

    def __call__(self, election_year, folder, type_of_date=datetime,
                 print_before_year="Election", quiet=False):
        Command.print_year(election_year, print_before_year, quiet)
        senate_election, _ = models.SenateElection.objects.get_or_create(
            election_date=type_of_date(year=election_year, month=1, day=1))
        [self.map_report_with_blank_line(
            direct, senate_election, False, single_meth, text_to_print) for
            direct, (single_meth, text_to_print) in zip(
            [os.path.join(folder, relative_directory) for relative_directory in
             Command.RELATIVE_DIRECTORIES], Command.MAPS)]

    def handle(self, *arguments, **keywordarguments):
        election_items = Command.get_election_items()
        [self(election_year, folder) for election_year, folder in
         election_items]

    @staticmethod
    def add_one_candidate(election, row):
        candidate, person = Command.find_person(
            models.SenateCandidate.objects,
            Command.get_standard_person_attributes(row), row)
        selection, _ = models.Selection.objects.get_or_create(
            person=person, election=election)
        selection.party = Command.fetch_party(row)
        selection.save()

    @staticmethod
    def add_source_preference(election, row):
        pool = models.Pool.objects.get(
            election=election, state=row['State'],
            vacancies=int(row['No Of Vacancies']),
            formal_papers=int(row['Total Formal Papers']),
            quota=int(row['Quota']))
        senate_round = models.SenateRound.objects.get(
            pool=pool, round_number=int(row['Count']))
        person_attributes = Command.get_standard_person_attributes(row)
        try:
            person = Command.fetch_by_aec_code(
                person_attributes, models.Person.objects,
                models.PersonCode.objects, 'person', int(
                    row[aec_codes.StringCode.CANDIDATE_CODE_HEADER]))
        except KeyError:
            person = models.Person.objects.get(**person_attributes)
        candidate = models.SenateCandidate.get(person=person)
        if candidate.group:
            assert candidate.group.abbreviation.lower().strip() == \
                   row[Command.ALTERNATIVE_GROUP_HEADER].lower().strip()
        try:
            ballot_position = int(row[Command.BALLOT_ORDER_HEADER])
        except KeyError:
            ballot_position = int(row[Command.ALTERNATIVE_BALLOT_ORDER_HEADER])
        senate_pref = models.SenatePreference.objects.get(
            round=senate_round, election=election, candidate=candidate,
            ballot_position=ballot_position,
            papers=int(row['Papers']),
            votes_transferred=int(row['VoteTransferred']),
            progressive_total=int(row['ProgressiveVoteTotal']),
            transfer_value=row['Transfer Value'],
            status=row['Status'],
            order_elected=row['Order Elected'],
            comment=row['Comment'])

    @staticmethod
    def add_one_preference(election, row):
        pool, _ = models.Pool.objects.get_or_create(
            election=election, state=row['State'],
            vacancies=int(row['No Of Vacancies']),
            formal_papers=int(row['Total Formal Papers']),
            quota=int(row['Quota']))
        senate_round, _ = models.SenateRound.objects.get_or_create(
            pool=pool, round_number=int(row['Count']))
        candidate, _ = Command.find_person(
            models.SenateCandidate.objects,
            Command.get_standard_person_attributes(row), row)
        if candidate.group:
            assert candidate.group.abbreviation.lower().strip() == \
                   row[Command.ALTERNATIVE_GROUP_HEADER].lower().strip()
        try:
            ballot_position = int(row[Command.BALLOT_ORDER_HEADER])
        except KeyError:
            ballot_position = int(row[Command.ALTERNATIVE_BALLOT_ORDER_HEADER])
        senate_pref, _ = models.SenatePreference.objects.get_or_create(
            round=senate_round, election=election, candidate=candidate,
            ballot_position=ballot_position,
            papers=int(row['Papers']),
            votes_transferred=int(row['VoteTransferred']),
            progressive_total=int(row['ProgressiveVoteTotal']),
            transfer_value=row['Transfer Value'],
            status=row['Status'],
            order_elected=row['Order Elected'],
            comment=row['Comment'])

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
        try:
            abbreviation = row['Group']
        except KeyError:
            abbreviation = row[Command.ALTERNATIVE_GROUP_HEADER]
        group, _ = models.SenateGroup.objects.get_or_create(
            abbreviation=abbreviation, election=election)
        candidate.group = group
        candidate.save()
        try:
            party, _ = models.Party.objects.get_or_create(name=row[
                aec_codes.StringCode.PARTY_NAME_HEADER])
        except models.Party.MultipleObjectsReturned:
            shortest = models.Party._meta.get_field('abbreviation').max_length
            for faction in models.Party.objects.filter(name=row[
                    aec_codes.StringCode.PARTY_NAME_HEADER]):
                abbreviation_length = len(faction.abbreviation)
                if abbreviation_length > 0:
                    if abbreviation_length < shortest:
                        shortest = abbreviation_length
                        party = faction
        try:
            selection = models.Selection.objects.get(person=candidate.person,
                                                     election=election)
        except models.Selection.DoesNotExist:
            selection = models.Selection.objects.create(
                person=candidate.person, election=election, party=party)
        vote_stack, _ = models.VoteStack.objects.get_or_create(
            floor=floor, election=election, lighthouse=lighthouse,
            candidate=candidate,
            state=row[aec_codes.StringCode.STATE_ABBREVIATION_HEADER].lower(),
            primary_votes=int(row[Command.ORDINARY_VOTES_HEADER]))
