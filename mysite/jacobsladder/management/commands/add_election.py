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


class StringCode(str):
    def __new__(cls, parts, parts_dictionary):
        return str.__new__(cls, "".join([parts_dictionary[part] if isinstance(
            part, super) else str(part) for part in parts]))

    #def __init__(self, parts, parts_dictionary, encoding=None, errors='strict'):
    #    str.__init__("".join([parts_dictionary[part] if
    #                          isinstance(part, super) else super(part)
    #                          for part in parts]), encoding, errors)

    @staticmethod
    def get_last_known(house_election, row):
        return StringCode(('CandidateID', 'PartyAb',
                           house_election.election_date.year), row)
        #return "".join([row['CandidateID'], row['PartyAb'], str(
        #    house_election.election_date.year)])


class Command(BaseCommand):
    FIRST_NAME_HEADER = 'Surname'

    help = 'Add elections from csv files'

    @staticmethod
    def walk(directory, file_extension=".csv"):
        for base_path, directories, files in os.walk(directory):
            for file in files:
                if file.endswith(file_extension):
                    yield os.path.join(base_path, file)

    @staticmethod
    def fetch_candid(house_election, row):
        return models.HouseCandidate.objects.get(
            person=models.Person.objects.get(name=row[
                Command.FIRST_NAME_HEADER],
                other_names=row['GivenNm'],
                last_known_codepartyyear=StringCode.get_last_known(
                    house_election, row))), \
            int(row['CalculationValue']), \
            models.Seat.objects.get(name=row['DivisionNm'],
                                    division_aec_code=row['DivisionID'])

    @staticmethod
    def fetch_transfer_data(current_round_numb, house_election, reader, row):
        candidate, received, seat = \
            Command.fetch_candid(house_election, row)
        remaining, transferred = \
            Command.advance(reader, received)
        return candidate, models.PreferenceRound.objects.get(
            seat=seat, election=house_election,
            round_number=current_round_numb), received, remaining, seat, \
            transferred

    @staticmethod
    def advance(reader, received):
        next(reader)
        transfer_row = next(reader)
        transferred = int(transfer_row['CalculationValue'])
        return received + transferred, transferred

    @staticmethod
    def add_source(candidate, current_round, house_election, pref_objects,
                   received, remaining, seat, transferred):
        pref = pref_objects.get(candidate=candidate, round=current_round,
                                election=house_election,
                                votes_received=received,
                                votes_transferred=transferred,
                                votes_remaining=remaining)
        pref.source_candidate = pref_objects.get(votes_received=0,
                                                 votes_transferred__lt=0,
                                                 round=current_round,
                                                 election=house_election,
                                                 seat=seat).candidate
        pref.save()

    @staticmethod
    def fetch_pref_data(house_election, reader, round_objects, row):
        candidate, received, seat = \
            Command.fetch_candid(house_election, row)
        remaining, transferred = Command.advance(
            reader, received)
        round_obj, _ = round_objects.get_or_create(
            seat=seat, election=house_election,
            round_number=int(row['CountNumber']))
        return candidate, round_obj, received, remaining, seat, \
            transferred

    @staticmethod
    def fetch_reader(filename, in_file):
        print(filename)
        next(in_file)
        return csv.DictReader(in_file)

    @staticmethod
    def fetch_candidate(house_election, row):
        person, _ = models.Person.objects.get_or_create(
            name=row['Surname'], other_names=row['GivenNm'],
            last_known_codepartyyear=StringCode.get_last_known(
                house_election, row))
        candidate, _ = models.HouseCandidate.objects.get_or_create(
            person=person)
        party, _ = models.Party.objects.get_or_create(
            name=row['PartyNm'], abbreviation=row['PartyAb'])
        return candidate, party, person

    @staticmethod
    def set_booths(house_election, row):
        booth, _ = models.Booth.objects.get_or_create(
            name=row['PollingPlace'],
            polling_place_aec_code=row['PollingPlaceID'])
        seat = models.Seat.objects.get(name=row['DivisionNm'],
                                       division_aec_code=row['DivisionID'])
        collection, _ = models.Collection.objects.get_or_create(
            booth=booth, seat=seat, election=house_election)
        return booth, seat

    @staticmethod
    def set_pref(house_election, pref_objects, reader, round_objects):
        row = next(reader)
        if row['CalculationType'] == 'Preference Count':
            candidate, pref_round, received, remaining, seat, \
                transferred = Command.fetch_pref_data(
                    house_election, reader, round_objects, row)

            #print("candidate", candidate)
            #print("pref_round", pref_round)
            #print("house_election", house_election)
            #print("received", received)
            #print("transferred", transferred)
            #print("remaining", remaining)
            #print("seat", seat)
            #print("round_objects", round_objects)



            pref, _ = pref_objects.get_or_create(candidate=candidate,
                                                 round=pref_round,
                                                 election=house_election,
                                                 votes_received=received,
                                                 votes_transferred=transferred,
                                                 votes_remaining=remaining)
            Command.update_pref(house_election, pref, seat)

    @staticmethod
    def add_tally(booth, candidate, house_election, party, person, row, seat):
        representation, _ = models.Representation.objects.get_or_create(
            person=person, party=party, election=house_election)
        contention, _ = models.Contention.objects.get_or_create(
            seat=seat, candidate=candidate,
            candidate_aec_code=row['CandidateID'],
            election=house_election,
            ballot_position=row['BallotPosition'])
        vote_tally, _ = models.VoteTally.objects.get_or_create(
            booth=booth, election=house_election,
            candidate=candidate,
            primary_votes=int(row['OrdinaryVotes']))

    @staticmethod
    def set_all_preferences(house_election, pref_objects, reader, round_objects):
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
                Command.set_all_preferences(house_election, pref_objects,
                                            self.fetch_reader(filename,
                                                              in_file),
                                            round_objects)

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
                                    candidate, current_round, received, \
                                        remaining, seat, transferred = \
                                        Command.fetch_transfer_data(
                                            current_round_numb,
                                            house_election, reader, row)
                                    if transferred > 0:
                                        Command.add_source(candidate,
                                                           current_round,
                                                           house_election,
                                                           pref_objects,
                                                           received,
                                                           remaining, seat,
                                                           transferred)
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
                    booth, seat = Command.set_booths(house_election, row)
                    candidate, party, person = Command.fetch_candidate(
                        house_election, row)
                    Command.add_tally(booth, candidate, house_election,
                                      party, person, row, seat)

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
                        name=row['Surname'],
                        other_names=row['GivenNm'],
                        last_known_codepartyyear=StringCode.get_last_known(
                            house_election, row))
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
                    enrollment, _ = models.Enrollment.objects.get_or_create(
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
