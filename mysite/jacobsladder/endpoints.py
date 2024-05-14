import json
from . import house, people, place, service


def getHousePrimaryVote(elections=None, parties=None, places=None, seats=True):
    party_set = people.Party.get_set(parties)
    place_set = place.Seat.get_set(places) if seats else place.Booth.get_set(
        places)
    result = {}
    for election in house.HouseElection.get_set(elections):
        election_result = {}
        representation_set = service.Representation.objects.filter(
            election=election, party__in=party_set)
        [election.update_election_result(election_result, representation_set,
                                         seat) for seat in place_set]
        result[str(election)] = election_result
    return json.dumps(result)


def getHousePrimaryVoteBySeat(elections=None, parties=None, places=None):
    return getHousePrimaryVote(elections, parties, places)


def getHousePrimaryVoteByBooth(elections=None, parties=None, places=None):
    return getHousePrimaryVote(elections, parties, places, False)



