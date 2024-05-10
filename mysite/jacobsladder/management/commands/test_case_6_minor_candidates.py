from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    help = "Get all the seats in 2022 where a non-Greens/ALP/Lib polled more " \
           "than 10% primary\n\n"

    AEC_RESULTS = {}

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)