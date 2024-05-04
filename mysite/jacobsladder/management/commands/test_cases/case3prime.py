from datetime import datetime
from django.core.management.base import BaseCommand
from .... import model_fields
from .... import models


class Command(BaseCommand):
    help = 'Case 3'

    def handle(self, *arguments, **keywordarguments):
        twenty_twenty_two = datetime(year=2022, month=1, day=1)
        house_election_2022 = models.HouseElection.objects.get(election_date=twenty_twenty_two)
        seat1 = models.Seat.objects.get(name="Aston", state=model_fields.StateName.VIC)
        models.Booth.per(Command.show_major_parties_candidate)(seat1, house_election_2022)

    @staticmethod
    def show_major_parties_candidate(election, seat, booth):
        print(booth)
        models.VoteTally.per(Command.show_candidate_if_major)(booth, seat, election)

    @staticmethod
    def show_candidate_if_major(election, seat, booth, vote_tally):
        if models.Representation.objects.filter(
                person=vote_tally.candidate.person,
                election=election).exists():
            abbreviation = models.Representation.objects.get(
                person=vote_tally.candidate.person,
                election=election).party.abbreviation
            if abbreviation in ('ALP', 'GRN', 'LP', ):
                print(f"{abbreviation}: {vote_tally.primary_votes}")
