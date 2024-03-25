from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = 'Case 1'

    def handle(self, *arguments, **keywordarguments):
        for election in models.HouseElection.objects.all().order_by(
                'election_date'):
            print(f"Election on {election.election_date}")
            for seat in election.seat_set.all():
                print(f"Seat of {seat.name}")
                for voteTally in models.VoteTally.objects.filter(
                        seat=seat, election=election):
                    if models.Representation.objects.filter(
                            election=election,
                            person=voteTally.candidate.person).exists():
                        middle = models.Representation.objects.get(
                            election=election,
                            person=voteTally.candidate.person).party.name
                    else:
                        middle = "Independent"
                    print(f"{voteTally.candidate.person.name}, {middle}, "
                          f"{voteTally.primary_votes}")
                print()
            print()




