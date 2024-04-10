from datetime import datetime
from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = 'Case 9'

    def handle(self, *arguments, **keywordarguments):
        twenty_ten = datetime(year=2010, month=1, day=1)
        house_election_2010 = models.HouseElection.objects.get(election_date=twenty_ten)
        seat1 = models.Seat.objects.get(name="Frank")
        hack_person = models.Person.objects.get(name="Party Hack")
        hack_candidate = models.HouseCandidate.objects.get(person=hack_person)
        print(f"Primary vote for {hack_person} in {house_election_2010}: "
              f"{seat1.primary_for(hack_candidate, house_election_2010)}")

