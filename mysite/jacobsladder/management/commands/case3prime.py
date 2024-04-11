from datetime import datetime
from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = 'Case 3'

    def handle(self, *arguments, **keywordarguments):
        twenty_ten = datetime(year=2010, month=1, day=1)
        house_election_2010 = models.HouseElection.objects.get(election_date=twenty_ten)
        seat1 = models.Seat.objects.get(name="Frank", state=models.StateName.VIC)
        models.Booth.per(Command.show_major_parties_primary)(seat1, house_election_2010)

    @staticmethod
    def show_major_parties_primary(election, seat, booth):
        print(booth)
        models.VoteTally.per(Command.show_primary_if_major)(booth, seat, election)

    @staticmethod
    def show_primary_if_major(election, seat, booth, vote_tally):
        if models.Representation.objects.filter(
                person=vote_tally.primary.person,
                election=election).exists():
            abbreviation = models.Representation.objects.get(
                person=vote_tally.primary.person,
                election=election).party.abbreviation
            if abbreviation in ('AAP', 'WTA', ):
                print(f"{abbreviation}: {vote_tally.primary_votes}")
