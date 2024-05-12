from django.core.management.base import BaseCommand

import mysite.jacobsladder.house
from ... import models


class Command(BaseCommand):
    help = 'Print primary votes by candidate for every booth in every seat in' \
           'every election in the house'

    def handle(self, *arguments, **keywordarguments):
        for election in mysite.jacobsladder.house.HouseElection.objects.all().order_by(
                'election_date'):
            print(f"Election on {election.election_date}")
            [Command.show_seat(election, seat) for seat in
             election.seat_set.all()]
            print()

    @staticmethod
    def show_seat(election, seat):
        print(f"\tSeat of {seat.name}")
        for booth in seat.booth_set.all():
            print(f"\t\t{booth}")
            models.VoteTally.per(Command.show_candidate)(
                booth, seat=seat, election=election)
        print()

    @staticmethod
    def show_candidate(election, seat, booth, vote_tally):
        if mysite.jacobsladder.house.Representation.objects.filter(
                election=election,
                person=vote_tally.candidate.person).exists():
            middle = mysite.jacobsladder.house.Representation.objects.get(
                election=election,
                person=vote_tally.candidate.person).party.name
        else:
            middle = "Independent"
        print(f"\t\t\t{vote_tally.candidate.person.name}, "
              f"{middle}, {vote_tally.primary_votes}")




