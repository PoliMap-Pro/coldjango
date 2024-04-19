import csv
import os

from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models

BOOTHS_DIRECTORY = ".\\jacobsladder\\2022\\prefs\\"
SEATS_DIRECTORY = ".\\jacobsladder\\2022\\votes_counted\\"
TWO_CANDIDATE_PREFERRED_DIRECTORY = ".\\jacobsladder\\2022\\" \
                                    "two_candidate_preferred\\"
PREFERENCE_DISTRIBUTION_DIRECTORY = ".\\jacobsladder\\2022\\" \
                                    "distribution_of_preferences\\"



class Command(BaseCommand):
    help = 'Add election from csv files'

    @staticmethod
    def walk(directory, file_extension=".csv"):
        for base_path, directories, files in os.walk(directory):
            for file in files:
                if file.endswith(file_extension):
                    yield os.path.join(base_path, file)

    def handle(self, *arguments, **keywordarguments):
        twenty_twenty_two = datetime(year=2022, month=1, day=1)
        house_election_2022, new_creation = \
            models.HouseElection.objects.get_or_create(
                election_date=twenty_twenty_two)
        print("Reading files in seats directory")
        for filename in Command.walk(SEATS_DIRECTORY):
            with open(filename, "r") as in_file:
                print(filename)
                next(in_file)   # skip the first row
                reader = csv.DictReader(in_file)
                for row in reader:
                    seat, _ = models.Seat.objects.get_or_create(
                        name=row['DivisionNm'], state=row['StateAb'].lower(),
                        division_aec_code=row['DivisionID'], enrollment=row['Enrolment'])
                    seat.elections.add(house_election_2022)
        print()
        print("Reading files in booths directory")
        for filename in Command.walk(BOOTHS_DIRECTORY):
            with open(filename, "r") as in_file:
                print(filename)
                next(in_file)
                reader = csv.DictReader(in_file)
                for row in reader:
                    booth, _ = models.Booth.objects.get_or_create(
                        name=row['PollingPlace'],
                        polling_place_aec_code=row['PollingPlaceID'])
                    seat = models.Seat.objects.get(name=row['DivisionNm'])
                    collection, _ = models.Collection.objects.get_or_create(
                        booth=booth, seat=seat, election=house_election_2022)
                    last_known_string = "".join([row['CandidateID'],
                                                 row['PartyAb'], str(
                            house_election_2022.election_date.year)])
                    person, _ = models.Person.objects.get_or_create(
                        name=row['Surname'], other_names=row['GivenNm'],
                        last_known_codepartyyear=last_known_string,
                    )
                    candidate, _ = models.HouseCandidate.objects.get_or_create(
                        person=person)
                    party, _ = models.Party.objects.get_or_create(
                        name=row['PartyNm'], abbreviation=row['PartyAb'])
                    representation, _ = \
                        models.Representation.objects.get_or_create(
                            person=person, party=party,
                            election=house_election_2022)
                    contention, _ = models.Contention.objects.get_or_create(
                        seat=seat, candidate=candidate,
                        candidate_aec_code=row['CandidateID'],
                        election=house_election_2022,
                        ballot_position=row['BallotPosition']
                    )
                    vote_tally, _ = models.VoteTally.objects.get_or_create(
                        booth=booth, election=house_election_2022,
                        candidate=candidate,
                        primary_votes=int(row['OrdinaryVotes']))
        print()
        print("Reading files in two candidate preferred directory")
        for filename in Command.walk(TWO_CANDIDATE_PREFERRED_DIRECTORY):
            with open(filename, "r") as in_file:
                print(filename)
                next(in_file)
                reader = csv.DictReader(in_file)
                for row in reader:
                    booth = models.Booth.objects.get(
                        name=row['PollingPlace'],
                        polling_place_aec_code=row['PollingPlaceID'])
                    person = models.Person.objects.get(
                        name=row['Surname'], other_names=row['GivenNm'],)
                    candidate = models.HouseCandidate.objects.get(
                        person=person)
                    vote_tally = models.VoteTally.objects.get(
                        booth=booth, election=house_election_2022,
                        candidate=candidate)
                    vote_tally.tcp_votes = int(row['OrdinaryVotes'])
                    vote_tally.save()
            print()
            print("Reading files in preference distribution directory")
            for filename in Command.walk(PREFERENCE_DISTRIBUTION_DIRECTORY):
                with open(filename, "r") as in_file:
                    print(filename)
                    next(in_file)
                    reader = csv.DictReader(in_file)
                    pref_objects = models.CandidatePreference.objects
                    #transfer_objects = models.VoteTransfer.objects
                    while True:
                        try:
                            row = next(reader)
                            if row['CalculationType'] == 'Preference Count':
                                seat = models.Seat.objects.get(name=row[
                                    'DivisionNm'])
                                pref_round, _ = \
                                    models.PreferenceRound.objects.get_or_create(
                                        seat=seat, election=house_election_2022,
                                        round_number=int(row['CountNumber'])
                                    )
                                person = models.Person.objects.get(
                                    name=row['Surname'],
                                    other_names=row['GivenNm'], )
                                candidate = models.HouseCandidate.objects.get(
                                    person=person)
                                received = int(row['CalculationValue'])
                                next(reader)
                                transfer_row = next(reader)
                                transferred = int(transfer_row['CalculationValue'])
                                remaining = received + transferred
                                pref, _ = pref_objects.get_or_create(
                                    candidate=candidate, round=pref_round,
                                    votes_received=received,
                                    votes_transferred=transferred,
                                    votes_remaining=remaining)
                        except StopIteration:
                            break
            # DO VOTETRANSFERS AND VOTEDISTRIBUTIONS
