import json
from . import house, people, place, service


def getHouseAttribute(elections=None, parties=None, places=None, seats=True,
                      tally_attribute='primary_votes', sum_booths=False):
    party_set, place_set, result = _setupHouseAttribute(parties, places, seats)
    [election.result_by_place(
        party_set, place_set, places, result, tally_attribute, sum_booths) for
     election in house.HouseElection.get_set(elections)]
    return json.dumps(result)


def getHousePrimaryVote(elections=None, parties=None, places=None, seats=True):
    return getHouseAttribute(elections, parties, places, seats)


def getHousePrimaryVoteBySeat(elections=None, parties=None, places=None):
    return getHousePrimaryVote(elections, parties, places)


def getHousePrimaryVoteByBooth(elections=None, parties=None, places=None):
    return getHousePrimaryVote(elections, parties, places, False)


def getHouseTwoPartyPreferred(elections=None, parties=None, places=None,
                              seats=True):
    return getHouseAttribute(elections, parties, places, seats, 'tcp_votes',
                             sum_booths=True)


def getHouseGeneralPartyPreferred(elections=None, places=None, seats=True,
                                  how_many=3, tally_attribute='primary_votes',
                                  sum_booths=False):
    party_set, place_set, result = _setupHouseAttribute(None, places, seats)
    [election.highest_by_votes(
        how_many, place_set, places, result, tally_attribute, sum_booths) for
        election in house.HouseElection.get_set(elections)]
    return json.dumps(result)


def _setupHouseAttribute(parties, places, seats):
    return people.Party.get_set(parties), place.Seat.get_set(
        places) if seats else None, {}



