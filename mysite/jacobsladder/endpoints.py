import json
from . import house, people, place, service


def getHouseAttribute(elections=None, parties=None, places=None, seats=True,
                      tally_attribute='primary_votes'):
    party_set = people.Party.get_set(parties)
    place_set = place.Seat.get_set(places) if seats else None
    result = {}
    [election.result_by_place(
        party_set, place_set, places, result, tally_attribute) for
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
    return getHouseAttribute(elections, parties, places, seats, 'tcp_votes')


def getHouseGeneralPartyPreferred(elections=None, places=None, seats=True,
                                  how_many=3):
    pass



