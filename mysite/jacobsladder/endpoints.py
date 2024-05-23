import json
from . import house, people, place, service, constants


def getHouseAttribute(elections=None, parties=None, places=None, seats=True,
                      tally_attribute='primary_votes', sum_booths=False,
                      return_format=constants.SPREADSHEET_FORMAT):
    """
    For each of elections, parties, places and seats either provide a list of
    django models or a dictionary of arguments for model.objects.filter() such
    as {'name': 'Chisholm', 'seat__name': 'Bean'} or
    {'abbreviation__in': ('GRN', 'ALP', 'LP')}
    """
    party_set, place_set, result = _setupHouseAttribute(parties, places, seats)
    [election.result_by_place(
        party_set, place_set, places, result, tally_attribute, sum_booths,
        return_format) for
     election in house.HouseElection.get_set(elections)]
    return json.dumps(result)


def getHousePrimaryVote(elections=None, parties=None, places=None, seats=True,
                        return_format=constants.SPREADSHEET_FORMAT):
    return getHouseAttribute(elections, parties, places, seats,
                             return_format=return_format)


def getHousePrimaryVoteBySeat(elections=None, parties=None, places=None,
                              return_format=constants.SPREADSHEET_FORMAT):
    return getHousePrimaryVote(elections, parties, places,
                               return_format=return_format)


def getHousePrimaryVoteByBooth(elections=None, parties=None, places=None,
                               return_format=constants.SPREADSHEET_FORMAT):
    return getHousePrimaryVote(elections, parties, places, False,
                               return_format=return_format)


def getHouseTwoPartyPreferred(elections=None, parties=None, places=None,
                              seats=True,
                              return_format=constants.SPREADSHEET_FORMAT):
    return getHouseAttribute(elections, parties, places, seats, 'tcp_votes',
                             sum_booths=True, return_format=return_format)


def getHouseGeneralPartyPreferred(elections=None, places=None, seats=True,
                                  how_many=3, tally_attribute='primary_votes',
                                  sum_booths=False,
                                  return_format=constants.SPREADSHEET_FORMAT):
    party_set, place_set, result = _setupHouseAttribute(None, places, seats)
    [election.highest_by_votes(
        how_many, place_set, places, result, tally_attribute, sum_booths) for
        election in house.HouseElection.get_set(elections)]
    return json.dumps(result)


def addMetaParties(**meta_parties):
    """
    Supply as parameters,
        name_of_meta_party_one = {'abbreviation__in': ('LP', 'NP')},
        name_of_meta_party_two = {'abbreviation__in': ('GRN', 'GVIC')},
        name_of_meta_party_three = {'name__contains': 'Australia'},
        etc.
    """

    for key, value in meta_parties.items():
        meta_party, _ = people.MetaParty.objects.get_or_create(name=key)
        for party in people.Party.objects.filter(**value):
            party.meta_parties.add(meta_party)


def getMetaParties():
    return json.dumps({meta_party.name: [
        str(party) for party in meta_party.party_set.all()] for meta_party in
        people.MetaParty.objects.all()})


def deleteMetaParties(*meta_parties):
    """
    Call with no parameters to delete all metaparties
    """

    if meta_parties:
        for meta_party_name in meta_parties:
            meta_party = people.MetaParty.objects.get(name=meta_party_name)
            meta_party.delete()
    else:
        for meta_party in people.MetaParty.objects.all():
            meta_party.delete()


def _setupHouseAttribute(parties, places, seats):
    """
    Fetches a query_set of Party models. If seats evaluates to True, also
    fetches a query_set of Seat models.
    """
    return people.Party.get_set(parties), place.Seat.get_set(
        places) if seats else None, {}



