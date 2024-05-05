from django.core.management.base import BaseCommand
from ... import models

"""
Use Cases
- Look at these N seats. How do preferences flow from the Libs to ALP/Greens in the 2016 election, and how about 2022 (where the Lib recommendation was different?)
- Get the top 10 greens seats by primary for each of the last 5 elections
- Get all the seats in 2022 where a non-Greens/ALP/Lib polled more than 10% primary
- How many voters put Greens in the top 3 for the senate in 2022.
"""


class Command(BaseCommand):
    help = ""

    AEC_RESULTS = {}

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        print("\n")




