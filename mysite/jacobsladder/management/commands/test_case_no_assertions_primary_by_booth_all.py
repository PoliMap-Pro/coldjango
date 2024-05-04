from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    help = 'Print primary votes by candidate for every booth in every seat in' \
           'every election in the house'

    def handle(self, *arguments, **keywordarguments):
        for election in models.HouseElection.objects.all().order_by(
                'election_date'):
            print(f"Election on {election.election_date}")
            for seat in election.seat_set.all():
                print(f"\tSeat of {seat.name}")
                for booth in seat.booth_set.all():
                    print(f"\t\t{booth}")
                    models.VoteTally.per(Command.show_candidate)(
                        booth, seat=seat, election=election)
                print()
            print()

    @staticmethod
    def show_candidate(election, seat, booth, vote_tally):
        if models.Representation.objects.filter(
                election=election,
                person=vote_tally.candidate.person).exists():
            middle = models.Representation.objects.get(
                election=election,
                person=vote_tally.candidate.person).party.name
        else:
            middle = "Independent"
        print(f"\t\t\t{vote_tally.candidate.person.name}, "
              f"{middle}, {vote_tally.primary_votes}")




