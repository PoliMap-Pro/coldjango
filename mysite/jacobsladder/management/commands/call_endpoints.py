from django.core.management.base import BaseCommand
from ... import place, house, endpoints


class Command(BaseCommand):
    help = "Calls functions in endpoints.py"

    def handle(self, *arguments, **keywordarguments):
        print(endpoints.getHousePrimaryVote(
            {'election_date__year__in': (2022, 2016, 2010)},
            {'abbreviation__in': ('GRN', 'ALP', 'LP')},
            {'name': 'Aston'}))
        print()
        print(endpoints.getHousePrimaryVote(
            {'election_date__year__in': (2019, 2013, 2007)},
            {'abbreviation__in': ('IND', 'UAPP')},
            {'name__in': ('Chisholm', 'Greenvale South')}))