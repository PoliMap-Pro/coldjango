from datetime import datetime
from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = 'Case 7'

    def handle(self, *arguments, **keywordarguments):
        twenty_twenty_two = datetime(year=2022, month=1, day=1)
        house_election_2022 = models.HouseElection.objects.get(
            election_date=twenty_twenty_two)

        def prime(election, seat):
            all_votes = seat.total_primary_votes(house_election_2022)
            for rep in models.Representation.objects.filter(election=election):
                if rep.party.abbreviation not in ('ALP', 'GRN', 'LP', ):
                    for contention in models.Contention.objects.filter(
                        election=house_election_2022,
                            seat=seat):
                        ratio = (seat.candidate_for(
                            contention.candidate, house_election_2022) /
                                 all_votes)
                        if ratio > 0.1:
                            return seat

        print(models.Seat.per(prime)(house_election_2022))


