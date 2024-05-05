from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    help = "What was the ALP and greens primary in Wills from 2001 - 2022?\n\n" \
           "Adds up the results from the booths and asserts that the totals " \
           "equal the number from https://results.aec.gov.au, which are: \n\n" \
           "('ALP', 2022): 25643, ('GRN', 2022): 18503 (https://results." \
           "aec.gov.au/24310/Website/HouseDivisionPage-24310-234.htm),\n" \
           "('ALP', 2019): 34021, ('GRN', 2019): 19994 (https://results." \
           "aec.gov.au/24310/Website/HouseDivisionPage-24310-234.htm),\n" \
           "('ALP', 2016): 28392, ('GRN', 2016): 22325 (https://results." \
           "aec.gov.au/20499/Website/HouseDivisionPage-20499-234.htm),\n" \
           "('ALP', 2013): 32873, ('GRN', 2013): 15244 (https://results." \
           "aec.gov.au/17496/Website/HouseDivisionFirstPrefsByVoteType-17496" \
           "-234.htm),\n" \
           "('ALP', 2010): 36964, ('GRN', 2010): 13436 (https://results." \
           "aec.gov.au/15508/Website/HouseDivisionFirstPrefsByVoteType-15508" \
           "-234.htm),\n" \
           "('ALP', 2007): 39963, ('GRN', 2007): 9044 (https://results." \
           "aec.gov.au/13745/Website/HouseDivisionFirstPrefsByVoteType-13745" \
           "-234.htm) and\n" \
           "('ALP', 2004): 37537, ('GRN', 2004): 8384 (https://results." \
           "aec.gov.au/12246/results/HouseDivisionFirstPrefsByVoteType-12246" \
           "-234.htm)"

    AEC_RESULTS = {('ALP', 2022): 25643, ('GRN', 2022): 18503,
                   ('ALP', 2019): 34021, ('GRN', 2019): 19994,
                   ('ALP', 2016): 28392, ('GRN', 2016): 22325,
                   ('ALP', 2013): 32873, ('GRN', 2013): 15244,
                   ('ALP', 2010): 36964, ('GRN', 2010): 13436,
                   ('ALP', 2007): 39963, ('GRN', 2007): 9044,
                   ('ALP', 2004): 37537, ('GRN', 2004): 8384, }

    def handle(self, *arguments, **keywordarguments):
        wills = models.Seat.objects.get(name="Wills", state="vic")
        print(Command.help)
        print("\n")
        for election in models.HouseElection.objects.all().order_by(
                'election_date'):
            print(f"Election on {election.election_date}")
            for party_abbreviation in ('ALP', 'GRN'):
                repre = models.Representation.objects.get(
                    election=election,
                    party__abbreviation__iexact=party_abbreviation,
                    person__candidate__contention__seat=wills,
                    person__candidate__contention__election=election
                )
                ordinary_primary = wills.candidate_for(
                    repre.person.candidate, election)
                assert ordinary_primary == Command.AEC_RESULTS[(
                    party_abbreviation, election.election_date.year, )]
                print(party_abbreviation, ordinary_primary)
            print()
