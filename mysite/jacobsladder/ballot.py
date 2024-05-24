from django.db.models import Sum

from . import service, place, constants, house


class Aggregator(object):
    BYPASSES = {'primary_votes': 'aec_total'}

    def fetch_total_aggregate_version(self, place, tally_attribute,
                                      return_format=constants.NEST_FORMAT):
        tallies = house.VoteTally.objects.filter(election=self, bypass=place)
        if tallies:
            if getattr(tallies[0], tally_attribute):
                attrib = tally_attribute
            else:
                attrib = Aggregator.BYPASSES[tally_attribute]
            aggregate = tallies.aggregate(Sum(attrib, default=0))
            if aggregate:
                if return_format == constants.TRANSACTION_FORMAT:
                    return aggregate.popitem()[1], tallies
                return aggregate.popitem()[1]
        if return_format == constants.TRANSACTION_FORMAT:
            return 0, tallies
        return 0

    def fetch_total_loop_version(self, place, tally_attribute):
        total = 0
        for vote_tally in house.VoteTally.objects.filter(
                election=self, bypass=place):
            change = getattr(vote_tally, tally_attribute)
            if change and (change > 0):
                total += change
            else:
                total += getattr(vote_tally, Aggregator.BYPASSES[
                    tally_attribute]) or 0
        return total


class Poll(Aggregator):
    def get_contentions(self, party_abbreviation):
        return [service.Contention.objects.get(
            election=self, candidate=representation.person.candidate) for
            representation in service.Representation.objects.filter(
                election=self, party__abbreviation=party_abbreviation)]

    def booths_for_election(self, place_set, places):
        election_result = {}
        if not place_set:
            place_set = place.Booth.get_set(self, places)
        return election_result, place_set

    def thin_representation_set(self, party_set, place_set):
        if isinstance(place_set[0], place.Seat):
            contention_set = service.Contention.objects.filter(
                election=self, seat__in=place_set)
        else:
            contention_set = service.Contention.objects.filter(
                election=self, seat__booth__in=place_set)
        return service.Representation.objects.filter(
            election=self, party__in=party_set,
            person__candidate__contention__in=contention_set).exclude(
            person__name__iexact=constants.INFORMAL_VOTER)

    def update_result(
            self, check_contentions, check_for_informal, election_result,
            name_of_informal_vote, place, representation_subset, result,
            return_format, tally_attribute, total):
        if check_for_informal:
            [place.update_place_result(
                self, representation, result, total, tally_attribute,
                return_format=return_format, election_result=election_result)
                for representation in representation_subset if
                representation.person.name.lower() != name_of_informal_vote]
        else:
            [place.update_place_result(
                self, representation, result, total, tally_attribute,
                return_format=return_format, election_result=election_result,
                check_contentions=check_contentions)
                for representation in representation_subset]