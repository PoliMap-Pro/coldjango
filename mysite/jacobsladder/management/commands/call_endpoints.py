from django.core.management.base import BaseCommand
from ... import endpoints


class Command(BaseCommand):
    help = "Calls functions in endpoints.py"

    def handle(self, *arguments, **keywordarguments):
        print(endpoints.getHousePrimaryVote(
            {'election_date__year__in': (2022, 2016, 2010)},
            {'abbreviation__in': ('GRN', 'ALP', 'LP')},
            {'name': 'Aston'}))
        print()
        print(endpoints.getHousePrimaryVote(
            {'election_date__year': 2022},
            {'abbreviation': 'ALP'},
            {'name': 'Chisholm', 'seat__name': 'Bean'},
            False))
        print()
        print(endpoints.getHousePrimaryVote(
            {'election_date__year': 2022},
            {'abbreviation': 'ALP'},
            {'name': 'Chisholm',},
            False))
        print()
        print(endpoints.getHouseTwoPartyPreferred(
            {'election_date__year__in': (2022, 2016, 2010)},
            {'abbreviation__in': ('GRN', 'ALP', 'LP')},
            {'name': 'Aston'}))
        print()
        print(endpoints.getHouseTwoPartyPreferred(
            {'election_date__year': 2022},
            {'abbreviation__in': ('GRN', 'ALP', 'LP')},
            {'name': 'Chisholm', 'seat__name': 'Bean'},
            False))
