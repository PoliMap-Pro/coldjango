from datetime import datetime

from django.core.management.base import BaseCommand
from ... import models

"""
Use Cases
- Show me the ALP/Lib primary for each booth in Aston in 2019
- Get me the Greens senate first pref vote in each seat, as well as the reps first pref vote, and calculate the delta. Do this over time from 2001
- Look at these N seats. How do preferences flow from the Libs to ALP/Greens in the 2016 election, and how about 2022 (where the Lib recommendation was different?)
- Get the top 10 greens seats by primary for each of the last 5 elections
- Get all the seats in 2022 where a non-Greens/ALP/Lib polled more than 10% primary
- How many voters put Greens in the top 3 for the senate in 2022.
"""

class Command(BaseCommand):
    help = "Show me the ALP/Lib primary for each booth in Aston in 2019"

    AEC_RESULTS = {('ALP', 2022): 25643, ('GRN', 2022): 18503,
                   ('ALP', 2019): 34021, ('GRN', 2019): 19994,
                   ('ALP', 2016): 28392, ('GRN', 2016): 22325,
                   ('ALP', 2013): 32873, ('GRN', 2013): 15244,
                   ('ALP', 2010): 36964, ('GRN', 2010): 13436,
                   ('ALP', 2007): 39963, ('GRN', 2007): 9044,
                   ('ALP', 2004): 37537, ('GRN', 2004): 8384, }

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        print("\n")
        twenty_nineteen = models.Election.objects.get(
            election_date=datetime(year=2022, month=1, day=1))
        aston = models.Seat.objects.get(name="Aston", state="vic")
        models.Booth.per(Command.primary)(aston, twenty_nineteen)

    @staticmethod
    def primary(election, seat, booth):
        for party_abbreviation in ('ALP', 'LP'):
            repre = models.Representation.objects.get(
                election=election,
                party__abbreviation__iexact=party_abbreviation,
                person__candidate__contention__seat=seat,
                person__candidate__contention__election=election
            )
            vote_tally = models.VoteTally.objects.get(
                booth=booth, election=election,
                candidate=repre.person.candidate
            )
            print(party_abbreviation, vote_tally.primary_votes)
