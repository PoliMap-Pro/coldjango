import csv
import os

from datetime import datetime
from operator import itemgetter

from django.core.management.base import BaseCommand
from ... import models

ELECTION_DIRECTORIES = {2022: ".\\jacobsladder\\2022\\",
                        2019: ".\\jacobsladder\\2019\\",
                        2016: ".\\jacobsladder\\2016\\",
                        2013: ".\\jacobsladder\\2013\\",
                        2010: ".\\jacobsladder\\2010\\",
                        2007: ".\\jacobsladder\\2007\\",
                        2004: ".\\jacobsladder\\2004\\", }

BOOTHS_DIRECTORY_RELATIVE = "prefs\\"
SEATS_DIRECTORY_RELATIVE = "votes_counted\\"
TWO_CANDIDATE_PREFERRED_DIRECTORY_RELATIVE = "two_candidate_preferred\\"
PREFERENCE_DISTRIBUTION_DIRECTORY_RELATIVE = "distribution_of_preferences\\"


class Command(BaseCommand):
    help = 'Add elections from csv files'

    @staticmethod
    def walk(directory, file_extension=".csv"):
        for base_path, directories, files in os.walk(directory):
            for file in files:
                if file.endswith(file_extension):
                    yield os.path.join(base_path, file)

    @staticmethod
    def fetch_candid(row):
        seat = models.Seat.objects.get(name=row[
            'DivisionNm'])
        person = models.Person.objects.get(
            name=row['Surname'],
            other_names=row['GivenNm'], )
        candidate = models.HouseCandidate.objects.get(
            person=person)
        return candidate, int(row['CalculationValue']), seat

    @staticmethod
    def advance(reader, received):
        next(reader)
        transfer_row = next(reader)
        transferred = int(transfer_row['CalculationValue'])
        return received + transferred, transferred

    @staticmethod
    def fetch_reader(filename, in_file):
        print(filename)
        next(in_file)
        return csv.DictReader(in_file)

    @staticmethod
    def start_election(election_year, folder):
        print("Election", election_year)
        print()
        election_date = datetime(year=election_year, month=1, day=1)
        house_election, _ = models.HouseElection.objects.get_or_create(
            election_date=election_date)
        return os.path.join(folder, BOOTHS_DIRECTORY_RELATIVE), \
            house_election, os.path.join(
            folder, PREFERENCE_DISTRIBUTION_DIRECTORY_RELATIVE), \
            os.path.join(folder, SEATS_DIRECTORY_RELATIVE), \
            os.path.join(folder, TWO_CANDIDATE_PREFERRED_DIRECTORY_RELATIVE)

    def first_pass_preferences(self, house_election, pref_objects,
                               preference_distribution_directory,
                               round_objects):
        print("First Pass: Reading files in preference "
              "distribution directory")
        for filename in Command.walk(preference_distribution_directory):
            with open(filename, "r") as in_file:
                reader = self.fetch_reader(filename, in_file)
                while True:
                    try:
                        row = next(reader)
                        if row['CalculationType'] == 'Preference Count':
                            candidate, received, seat = \
                                Command.fetch_candid(row)
                            pref_round, _ = \
                                round_objects.get_or_create(
                                    seat=seat, election=house_election,
                                    round_number=int(row['CountNumber']))
                            remaining, transferred = Command.advance(
                                reader, received)
                            pref, _ = pref_objects.get_or_create(
                                candidate=candidate, round=pref_round,
                                election=house_election,
                                votes_received=received,
                                votes_transferred=transferred,
                                votes_remaining=remaining)
                            if not pref.seat:
                                pref.seat = seat
                                pref.save()
                            if not pref.election:
                                pref.election = house_election
                                pref.save()
                    except StopIteration:
                        break

    def second_pass_preferences(self, house_election, pref_objects,
                                preference_distribution_directory):
        print()
        print("Second Pass: Reading files in preference "
              "distribution directory")
        for filename in Command.walk(preference_distribution_directory):
            with open(filename, "r") as in_file:
                reader = self.fetch_reader(filename, in_file)
                while True:
                    try:
                        row = next(reader)
                        if row['CalculationType'] == 'Preference Count':
                            if int(row['CalculationValue']) > 0:
                                current_round_numb = int(
                                    row['CountNumber'])
                                if current_round_numb > 0:
                                    candidate, received, seat = \
                                        Command.fetch_candid(row)
                                    current_round = \
                                        models.PreferenceRound.objects.get(
                                            seat=seat,
                                            election=house_election,
                                            round_number=current_round_numb)
                                    remaining, transferred = \
                                        Command.advance(reader, received)
                                    if transferred > 0:
                                        pref = pref_objects.get(
                                            candidate=candidate,
                                            round=current_round,
                                            election=house_election,
                                            votes_received=received,
                                            votes_transferred=transferred,
                                            votes_remaining=remaining
                                        )
                                        source_pref = pref_objects.get(
                                            votes_received=0,
                                            votes_transferred__lt=0,
                                            round=current_round,
                                            election=house_election,
                                            seat=seat)
                                        pref.source_candidate = \
                                            source_pref.candidate
                                        pref.save()
                    except StopIteration:
                        print()
                        break

    def add_booths(self, booths_directory, house_election):
        print()
        print("Reading files in booths directory")
        for filename in Command.walk(booths_directory):
            with open(filename, "r") as in_file:
                reader = self.fetch_reader(filename, in_file)
                for row in reader:
                    booth, _ = models.Booth.objects.get_or_create(
                        name=row['PollingPlace'],
                        polling_place_aec_code=row['PollingPlaceID'])
                    seat = models.Seat.objects.get(
                        name=row['DivisionNm'],
                        division_aec_code=row['DivisionID'])
                    collection, _ = models.Collection.objects.get_or_create(
                        booth=booth, seat=seat, election=house_election)
                    last_known_string = "".join([row['CandidateID'],
                                                 row['PartyAb'], str(
                            house_election.election_date.year)])
                    person, _ = models.Person.objects.get_or_create(
                        name=row['Surname'], other_names=row['GivenNm'],
                        last_known_codepartyyear=last_known_string)
                    candidate, _ = \
                        models.HouseCandidate.objects.get_or_create(
                            person=person)
                    party, _ = models.Party.objects.get_or_create(
                        name=row['PartyNm'], abbreviation=row['PartyAb'])
                    representation, _ = \
                        models.Representation.objects.get_or_create(
                            person=person, party=party,
                            election=house_election)
                    contention, _ = models.Contention.objects.get_or_create(
                        seat=seat, candidate=candidate,
                        candidate_aec_code=row['CandidateID'],
                        election=house_election,
                        ballot_position=row['BallotPosition'])
                    vote_tally, _ = models.VoteTally.objects.get_or_create(
                        booth=booth, election=house_election,
                        candidate=candidate,
                        primary_votes=int(row['OrdinaryVotes']))

    def add_votes(self, house_election, two_candidate_preferred_directory):
        print()
        print("Reading files in two candidate preferred directory")
        for filename in Command.walk(two_candidate_preferred_directory):
            with open(filename, "r") as in_file:
                reader = self.fetch_reader(filename, in_file)
                for row in reader:
                    booth = models.Booth.objects.get(
                        name=row['PollingPlace'],
                        polling_place_aec_code=row['PollingPlaceID'])
                    person = models.Person.objects.get(
                        name=row['Surname'], other_names=row['GivenNm'], )
                    candidate = models.HouseCandidate.objects.get(
                        person=person)
                    vote_tally = models.VoteTally.objects.get(
                        booth=booth, election=house_election,
                        candidate=candidate)
                    vote_tally.tcp_votes = int(row['OrdinaryVotes'])
                    vote_tally.save()
            print()

    def add_seats(self, house_election, seats_directory):
        print("Reading files in seats directory")
        for filename in Command.walk(seats_directory):
            with open(filename, "r") as in_file:
                reader = self.fetch_reader(filename, in_file)
                for row in reader:
                    seat, _ = models.Seat.objects.get_or_create(
                        name=row['DivisionNm'],
                        state=row['StateAb'].lower(),
                        division_aec_code=row['DivisionID'])
                    seat.elections.add(house_election)
                    enrollment, _ = \
                        models.Enrollment.objects.get_or_create(
                            seat=seat, election=house_election,
                            number_enrolled=int(row['Enrolment']))

    def handle(self, *arguments, **keywordarguments):
        pref_objects = models.CandidatePreference.objects
        round_objects = models.PreferenceRound.objects
        election_items = list(ELECTION_DIRECTORIES.items())
        election_items.sort(key=itemgetter(0))
        election_items.reverse()
        for election_year, folder in election_items:
            booths_directory, house_election, \
                preference_distribution_directory, \
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










