from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    help = "Get the top 10 greens seats by primary for each of " \
           "the last 5 elections\n\n"

    AEC_RESULTS = {}

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        print("\n")




