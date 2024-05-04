from django.core.management.base import BaseCommand
from ... import models

"""
Use Cases
- What are the 20 most marginal federal seats? (seats where winner tpp-50 is smallest)
- Show me the ALP/Lib primary for each booth in Aston in 2019
- Get me the Greens senate first pref vote in each seat, as well as the reps first pref vote, and calculate the delta. Do this over time from 2001
- Look at these N seats. How do preferences flow from the Libs to ALP/Greens in the 2016 election, and how about 2022 (where the Lib recommendation was different?)
- Get the top 10 greens seats by primary for each of the last 5 elections
- Get all the seats in 2022 where a non-Greens/ALP/Lib polled more than 10% primary
- How many voters put Greens in the top 3 for the senate in 2022.
"""

class Command(BaseCommand):
    help = 'What was the ALP and greens primary in Wills from 2001 - 2022?'

    AEC_RESULTS = {
#https://results.aec.gov.au/27966/Website/HouseDivisionPage-27966-234.htm
        ('ALP', 2022): 25643, ('GRN', 2022): 18503,

#https://results.aec.gov.au/24310/Website/HouseDivisionPage-24310-234.htm
        ('ALP', 2019): 34021, ('GRN', 2019): 19994,

#https://results.aec.gov.au/20499/Website/HouseDivisionPage-20499-234.htm
        ('ALP', 2016): 28392, ('GRN', 2016): 22325,

#/17496/Website/HouseDivisionFirstPrefsByVoteType-17496-234.htm
        ('ALP', 2013): 32873, ('GRN', 2013): 15244,

#/15508/Website/HouseDivisionFirstPrefsByVoteType-15508-234.htm
        ('ALP', 2010): 36964, ('GRN', 2010): 13436,

#/13745/Website/HouseDivisionFirstPrefsByVoteType-13745-234.htm
        ('ALP', 2007): 39963, ('GRN', 2007): 9044,

#/12246/results/HouseDivisionFirstPrefsByVoteType-12246-234.htm
        ('ALP', 2004): 37537, ('GRN', 2004): 8384,
    }

    def handle(self, *arguments, **keywordarguments):
        wills = models.Seat.objects.get(name="Wills", state="vic")
        for election in models.HouseElection.objects.all().order_by(
                'election_date'):
            print(f"Election on {election.election_date}")
            for party_abbreviation in ('ALP', 'GRN'):
                alp_representation = models.Representation.objects.get(
                    election=election,
                    party__abbreviation__iexact=party_abbreviation,
                    person__candidate__contention__seat=wills,
                    person__candidate__contention__election=election
                )
                ordinary_primary = wills.candidate_for(
                    alp_representation.person.candidate, election)
                assert ordinary_primary == Command.AEC_RESULTS[(
                    party_abbreviation, election.election_date.year, )]
                print(party_abbreviation, ordinary_primary)
            print()
