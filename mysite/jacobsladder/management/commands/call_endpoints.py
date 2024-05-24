import pprint
from django.core.management.base import BaseCommand
from ... import endpoints
import cProfile


class Command(BaseCommand):
    help = "Calls functions in endpoints.py"

    def handle(self, *arguments, **keywordarguments):
        pprint.pp(endpoints.getHousePrimaryVote(
            {'election_date__year__in': (2022, 2016, 2010)},
            {'abbreviation__in': ('GRN', 'ALP', 'LP')},
            {'name': 'Aston'}, ))
        exit()
        with cProfile.Profile() as pr:
            pprint.pp(endpoints.getHousePrimaryVote(
                {'election_date__year__in': (2022, 2016, 2010)},
                {'abbreviation__in': ('GRN', 'ALP', 'LP')},
                {'name': 'Aston'}, ))
            pr.print_stats()
        exit()
        print()
        pprint.pp(endpoints.getHousePrimaryVote(
            {'election_date__year': 2022},
            {'abbreviation': 'ALP'},
            {'name': 'Chisholm', 'seat__name': 'Bean'},
            False))
        print()
        pprint.pp(endpoints.getHousePrimaryVote(
            {'election_date__year': 2022},
            {'abbreviation': 'ALP'},
            {'name': 'Chisholm',},
            False))
        print()
        pprint.pp(endpoints.getHouseTwoPartyPreferred(
            {'election_date__year__in': (2022, 2016, 2010)},
            {'abbreviation__in': ('GRN', 'ALP', 'LP')},
            {'name': 'Aston'}))
        print()
        pprint.pp(endpoints.getHouseTwoPartyPreferred(
            {'election_date__year': 2022},
            {'abbreviation__in': ('GRN', 'ALP', 'LP')},
            {'name': 'Chisholm', 'seat__name': 'Bean'},
            False))
        print()
        pprint.pp(endpoints.getHouseGeneralPartyPreferred(
            {'election_date__year__in': (2022, 2016, 2010)},
            {'name': 'Aston'},
            how_many=3))
        pprint.pp(endpoints.getMetaParties())
        print()
        endpoints.addMetaParties(
            Libnat={'abbreviation__in': ('LP', 'NP')},
            Green={'abbreviation__in': ('GRN', 'GVIC')},
        )
        pprint.pp(endpoints.getMetaParties())
        print()
        endpoints.deleteMetaParties('Libnat')
        print()
        pprint.pp(endpoints.getMetaParties())
        print()
        endpoints.addMetaParties(Aus={'name__icontains': 'aus'})
        pprint.pp(endpoints.getMetaParties())
        print()
        endpoints.deleteMetaParties()
        pprint.pp(endpoints.getMetaParties())
        endpoints.addMetaParties(
            Libnat={'abbreviation__in': ('LP', 'NP')},
            Green={'abbreviation__in': ('GRN', 'GVIC')},
        )
        pprint.pp(endpoints.getHousePrimaryVote(
            {'election_date__year__in': (2022, 2016, )},
            {'meta_parties__name': 'Libnat'},
            {'state__iexact': 'Vic'}))
        print()
