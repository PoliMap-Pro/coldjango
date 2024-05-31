from django.core.management.base import BaseCommand
from ... import house, place, people, endpoints


class Command(BaseCommand):
    help = "writes dataset json"
    seat_attributes = ("primary_votes", "aec_ordinary", "postal_votes",
                       "declaration_pre_poll_votes", )

    ALP_ABBREVIATIONS = ['ALP', ]
    COALITION_ABBREVIATIONS = ['LNQ', 'LP', 'LNP', 'CLP', 'NP']
    GREEN_ABBREVIATIONS = ['GRN', 'GVIC', ]
    LIBERAL_ABBREVIATIONS = ['LP', 'LNQ', 'LNP', 'CLP' ]
    NATIONALS_ABBREVIATIONS = ['NP', 'LNQ', ]

    parties = {
        "ALP": ({'abbreviation__in': ALP_ABBREVIATIONS}, None),
        "Coalition": ({'abbreviation__in': COALITION_ABBREVIATIONS}, None),
        "Greens": ({'abbreviation__in': GREEN_ABBREVIATIONS}, None),
        "Independents": ({'abbreviation': 'IND'}, None),
        "Liberals": ({'abbreviation__in': LIBERAL_ABBREVIATIONS}, None),
        "Nationals": ({'abbreviation__in': NATIONALS_ABBREVIATIONS}, None),
        "Other": (None, {
            'abbreviation__in': ALP_ABBREVIATIONS + COALITION_ABBREVIATIONS}),
        "Minors": (None, {'abbreviation__in': GREEN_ABBREVIATIONS +
                          ALP_ABBREVIATIONS + COALITION_ABBREVIATIONS}),}

    def handle(self, *arguments, **keyword_arguments):
        data_set_id = 1003
        out_lines = []
        for election in house.HouseElection.objects.all():
            for key, (yes, no) in Command.parties.items():
                print(election.election_date.year, yes, no)
                parties = Command.get_parties(no, yes)
                if parties:
                    party, party_data = Command.get_party_data(
                        no, parties, parties[0], yes)
                    data_set_id = Command.get_data_sets(
                        data_set_id, election, key, out_lines, party,
                        party_data)
                    with open("./jsondatasets.txt", "a") as outfile:
                        outfile.writelines(out_lines)
                    out_lines = []

    @staticmethod
    def get_data_sets(data_set_id, election, key, out_lines, party,
                      party_data):
        data_set_id = Command.seat_set(
            data_set_id, election, key, out_lines, party,
            party_data)
        data_set_id = Command.booth_set(
            data_set_id, election, key, out_lines, party,
            party_data)
        return Command.tcp_set(
            data_set_id, election, key, out_lines, party,
            party_data)

    @staticmethod
    def tcp_set(data_set_id, election, key, out_lines, party, party_data):
        #data = endpoints.getHouseTwoPartyPreferred(
        #    elections=[election, ],
        #    parties=party_data,
        #    seats=True)
        #if data['series'][0]['data']:
        Command.add_out_line(
            data_set_id, election, key, out_lines, party, "tcp_votes", "",
            seats_bool=True, party_data=party_data)
        data_set_id += 1
        return data_set_id

    @staticmethod
    def booth_set(data_set_id, election, key, out_lines, party, party_data):
        #data = endpoints.getHouseAttribute(
        #    elections=[election, ],
        #    parties=party_data,
        #    seats=False,
        #    tally_attribute="primary_votes")
        #if data['series'][0]['data']:
        Command.add_out_line(
            data_set_id, election, key, out_lines, party,
            "primary_votes", "", seats_bool=False,
            party_data=party_data, name_final="Booth")
        data_set_id += 1
        return data_set_id

    @staticmethod
    def seat_set(data_set_id, election, key, out_lines, party, party_data):
        for tally_attr in Command.seat_attributes:
            #data = endpoints.getHouseAttribute(
            #    elections=[election, ],
            #    parties=party_data,
            #    seats=True,
            #    tally_attribute=tally_attr)
            #if data['series'][0]['data']:
            Command.add_out_line(
                data_set_id, election, key, out_lines, party, tally_attr,
                "", seats_bool=True, party_data=party_data)
            data_set_id += 1
        return data_set_id

    @staticmethod
    def get_party_data(no, parties, party, yes):
        if yes and not no:
            party_data = yes
        else:
            abbr_list = []
            for party in parties:
                if party.abbreviation:
                    if party.abbreviation not in abbr_list:
                        abbr_list.append(party.abbreviation)
            abbr_list.sort()
            party_data = {'abbreviation__in': abbr_list}
        return party, party_data

    @staticmethod
    def get_parties(no, yes):
        if yes:
            parties = people.Party.objects.filter(**yes)
        else:
            parties = people.Party.objects.all()
        if no:
            parties = parties.exclude(**no)
        return parties

    @staticmethod
    def add_out_line(
            data_set_id, election, key, out_lines, party, tally_attr, seat,
            seats_bool=False, party_data="", name_final="CED"):
        if seat:
            name_string, place_string = f"/{seat}", f" {seat}"
            places_selector = f"{{'name': \\\"{seat}\\\"}}"
        else:
            name_string, place_string, places_selector = "", "", ""
        out_lines.append(f"""
    {{
        "id": {data_set_id},
        "name": "/AEC/Election/{election.election_date.year}/{tally_attr}/{key}{name_string}/{name_final}",
        "display_name": "{tally_attr} {key} (percent)",
        "type": "region",
        "level": "CED",
        "series_name": "{election.election_date.year} {party.abbreviation if party.abbreviation else ""}{place_string} {tally_attr}",
        "data": [],
        "source": {{
            "name": "AEC",
            "url": "https://www.aec.gov.au/",
            "dataset": "Federal Election {election.election_date.year}"
        }},
        "query": {{
            "query_type": "elecdata",
            "query_text": {{
                tally_attribute: "{tally_attr}",
                elections: {{'election_date__year': {election.election_date.year}}},
                parties: {party_data},
                seats: "{seats_bool}"
            }},
            "filter": {{
                'places': "{places_selector}"
            }},
        }},
    }},
                                    """)


"""
I remembered that I wrote this on the plane on the way over.

# Datasets for Andy to sort out.

Note: CED = Cwth electoral district = lower house seat

parties =  Greens, Liberals, Nationals, ALP, Coalition, Independents,
Other(=not coalition, ALP), Minors(=not ALP/Coalition/Greens)
### 1. Primary vote
For each house election:
	For each party in parties:
		For each seat (as %):
			primary vote
			ordinary votes
			postal votes
			prepoll votes
            for each booth:
                primary vote (ordinary votes)

Datasets can have multiple *names*. These datasets will each have the
following names:

Where vote type in "primary", "ordinary, "postal", "prepoll":

`AEC/Elections/House/year/<vote type>/<party>/CED`
`AEC/Elections/House/year/<vote type>/<party>/booth`
`AEC/Elections/House/series/` XX

The readable description is f"{party} lower house {vote_type} {year}"

### 2. TPP vote
`AEC/Elections/House/year/TPP/CED`
"""