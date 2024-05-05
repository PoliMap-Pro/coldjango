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
    help = "Show me the ALP/Lib primary for each booth in Aston in 2019\n\n" \
           ""

    AEC_RESULTS = {('ALP', 'Bayswater'): 724,
                   ('LP', 'Bayswater'): 880,

                   ('ALP', 'Bayswater South'): 225,
                   ('LP', 'Bayswater South'): 301,

                   ('ALP', 'Bayswater West'): 417,
                   ('LP', 'Bayswater West'): 607,

                   ('ALP', 'Blackwood Park'): 265,
                   ('LP', 'Blackwood Park'): 357,

                   ('ALP', 'BLV Aston PPVC'): 11,
                   ('LP', 'BLV Aston PPVC'): 11,

                   ('ALP', 'Boronia'): 534,
                   ('LP', 'Boronia'): 692,

                   ('ALP', 'Boronia ASTON PPVC'): 4166,
                   ('LP', 'Boronia ASTON PPVC'): 7040,

                   ('ALP', 'Boronia East'): 360,
                   ('LP', 'Boronia East'): 392,

                   ('ALP', 'Boronia North'): 477,
                   ('LP', 'Boronia North'): 665,

                   ('ALP', 'Divisional Office (PREPOLL)'): 267,
                   ('LP', 'Divisional Office (PREPOLL)'): 929,

                   ('ALP', 'Fairhills'): 466,
                   ('LP', 'Fairhills'): 604,

                   ('ALP', 'Ferntree Gully'): 302,
                   ('LP', 'Ferntree Gully'): 358,

                   ('ALP', 'Ferntree Gully North'): 452,
                   ('LP', 'Ferntree Gully North'): 528,

                   ('ALP', 'Ferntree Gully West'): 552,
                   ('LP', 'Ferntree Gully West'): 792,

                   ('ALP', 'Heany Park'): 910,
                   ('LP', 'Heany Park'): 1550,

                   ('ALP', 'Karoo'): 594,
                   ('LP', 'Karoo'): 1460,

                   ('ALP', 'Kent Park'): 275,
                   ('LP', 'Kent Park'): 439,

                   ('ALP', 'Knoxfield'): 483,
                   ('LP', 'Knoxfield'): 819,

                   ('ALP', 'Knox Gardens'): 621,
                   ('LP', 'Knox Gardens'): 1163,

                   ('ALP', 'Lysterfield'): 492,
                   ('LP', 'Lysterfield'): 1327,

                   ('ALP', 'Mountain Gate'): 675,
                   ('LP', 'Mountain Gate'): 1065,

                   ('ALP', 'Park Ridge'): 515,
                   ('LP', 'Park Ridge'): 939,

                   ('ALP', 'Rowville'): 515,
                   ('LP', 'Rowville'): 851,

                   ('ALP', 'Rowville Central'): 294,
                   ('LP', 'Rowville Central'): 603,

                   ('ALP', 'Rowville East'): 262,
                   ('LP', 'Rowville East'): 500,

                   ('ALP', 'Rowville North'): 174,
                   ('LP', 'Rowville North'): 258,

                   ('ALP', 'Rowville PPVC'): 3082,
                   ('LP', 'Rowville PPVC'): 7672,

                   ('ALP', 'Scoresby'): 674,
                   ('LP', 'Scoresby'): 1085,

                   ('ALP', 'Special Hospital Team 1'): 35,
                   ('LP', 'Special Hospital Team 1'): 69,

                   ('ALP', 'Special Hospital Team 2'): 46,
                   ('LP', 'Special Hospital Team 2'): 121,

                   ('ALP', 'Special Hospital Team 3'): 82,
                   ('LP', 'Special Hospital Team 3'): 160,

                   ('ALP', 'Special Hospital Team 4'): 27,
                   ('LP', 'Special Hospital Team 4'): 121,

                   ('ALP', 'Studfield East'): 462,
                   ('LP', 'Studfield East'): 691,

                   ('ALP', 'Templeton'): 448,
                   ('LP', 'Templeton'): 643,

                   ('ALP', 'The Basin'): 508,
                   ('LP', 'The Basin'): 676,

                   ('ALP', 'Upper Ferntree Gully (Aston)'): 329,
                   ('LP', 'Upper Ferntree Gully (Aston)'): 340,

                   ('ALP', 'Wantirna'): 505,
                   ('LP', 'Wantirna'): 900,

                   ('ALP', 'Wantirna Central'): 565,
                   ('LP', 'Wantirna Central'): 1056,

                   ('ALP', 'Wantirna South'): 365,
                   ('LP', 'Wantirna South'): 617,

                   ('ALP', 'Wantirna South PPVC'): 2561,
                   ('LP', 'Wantirna South PPVC'): 5308,

                   ('ALP', 'Wantirna West'): 377,
                   ('LP', 'Wantirna West'): 756,

                   ('ALP', 'Watersedge'): 357,
                   ('LP', 'Watersedge'): 632, }

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        print("\n")
        twenty_nineteen = models.HouseElection.objects.get(
            election_date=datetime(year=2019, month=1, day=1))
        aston = models.Seat.objects.get(name="Aston", state="vic")
        models.Booth.per(Command.primary)(aston, twenty_nineteen)

    @staticmethod
    def primary(election, seat, booth):
        print(booth)
        for party_abbreviation in ('ALP', 'LP'):
            repre = models.Representation.objects.get(
                election=election,
                party__abbreviation__iexact=party_abbreviation,
                person__candidate__contention__seat=seat,
                person__candidate__contention__election=election
            )
            try:
                vote_tally = models.VoteTally.objects.get(
                    booth=booth, election=election,
                    candidate=repre.person.candidate
                )
                primary_votes = vote_tally.primary_votes
                assert primary_votes == Command.AEC_RESULTS[(
                    party_abbreviation, booth.name, )]
                print(party_abbreviation, vote_tally.primary_votes)
            except models.VoteTally.DoesNotExist:
                print(party_abbreviation, "DID NOT RUN A CANDIDATE")
        print()
