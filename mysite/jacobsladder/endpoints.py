import json
from . import house, people, place, service


def getHousePrimaryVote(elections=None, parties=None, seats=None):
    party_set = people.Party.get_set(parties)
    seat_set = place.Seat.get_set(seats)
    result = {}
    for election in house.HouseElection.get_set(elections):
        election_result = {}
        representation_set = service.Representation.objects.filter(
            election=election, party__in=party_set)
        [election.update_election_result(election_result, representation_set,
                                         seat) for seat in seat_set]
        result[str(election)] = election_result
    return json.dumps(result)





