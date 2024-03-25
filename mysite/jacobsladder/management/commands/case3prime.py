from datetime import datetime
from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = 'Case 3'

    def handle(self, *arguments, **keywordarguments):
        twenty_ten = datetime(year=2010, month=1, day=1)
        house_election_2010 = models.HouseElection.objects.get(election_date=twenty_ten)
        seat1 = models.Seat.objects.get(name="Frank", state=models.StateName.VIC)
        if models.Booth.objects.all().count() < 5:
            booth5 = models.Booth()
            booth5.save()
            collection5 = models.Collection(booth=booth5, seat=seat1,
                                            election=house_election_2010)
            collection5.save()
