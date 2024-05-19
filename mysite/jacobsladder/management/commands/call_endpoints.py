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
        print()
        print(endpoints.getHouseGeneralPartyPreferred(
            {'election_date__year__in': (2022, 2016, 2010)},
            {'name': 'Aston'},
            how_many=3))

        print(endpoints.getMetaParties())
        print()
        endpoints.addMetaParties(
            Libnat={'abbreviation__in': ('LP', 'NP')},
            Green={'abbreviation__in': ('GRN', 'GVIC')},
        )
        print(endpoints.getMetaParties())
        print()
        endpoints.deleteMetaParties('Libnat')
        print()
        print(endpoints.getMetaParties())
        print()
        endpoints.addMetaParties(Aus={'name__icontains': 'aus'})
        print(endpoints.getMetaParties())
        print()
        endpoints.deleteMetaParties()
        print(endpoints.getMetaParties())
        endpoints.addMetaParties(
            Libnat={'abbreviation__in': ('LP', 'NP')},
            Green={'abbreviation__in': ('GRN', 'GVIC')},
        )
        print(endpoints.getHousePrimaryVote(
            {'election_date__year__in': (2022, 2016, )},
            {'meta_parties__name': 'Libnat'},
            {'state__iexact': 'Vic'}))
        print()
