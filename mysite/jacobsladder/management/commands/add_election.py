import csv
import os

from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models

BOOTHS_DIRECTORY = ".\\jacobsladder\\2022\\prefs\\"
SEATS_FILE = r".\jacobsladder\2022\votes_counted\housevotescountedbydivisiondownload-27966.csv"


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
        with open(SEATS_FILE, "r") as in_file:
            print(SEATS_FILE)
            next(in_file)   # skip the first row
            reader = csv.DictReader(in_file)
            for row in reader:
                seat, _ = models.Seat.objects.get_or_create(
                    name=row['DivisionNm'], state=row['StateAb'].lower(),
                    division_aec_code=row['DivisionID'], enrollment=row['Enrolment'])
                seat.elections.add(house_election_2022)
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


