from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    help = "How many voters put Greens in the top 3 for the senate in " \
           "2022.\n\n"

    AEC_RESULTS = {}

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        twenty_twenty_two = models.SenateElection.objects.get(
            election_date=datetime(year=2022, month=1, day=1))
