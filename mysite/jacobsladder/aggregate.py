from django.db.models import Sum
from . import constants, house


class Aggregator(object):
    BYPASSES = {'primary_votes': 'aec_total'}

    def setup_source(self, election, last_preference, preference_rounds,
                     target_index):
        return house.CandidatePreference.objects.get(
            election=election, seat=self,
            candidate=last_preference.source_candidate,
            round=preference_rounds[target_index]), \
               house.CandidatePreference.objects.get(
                   election=election, seat=self,
                   candidate=last_preference.source_candidate,
                   round=preference_rounds[target_index-1])

    def fetch_total_aggregate_version(self, place, tally_attribute,
                                      return_format=constants.NEST_FORMAT):
        tallies = house.VoteTally.objects.filter(election=self, bypass=place)
        if tallies:
            aggregate = Aggregator.set_aggregate(tallies, tally_attribute)
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
            total = Aggregator.increase_loop_total(tally_attribute, total,
                                                   vote_tally)
        return total

    def total_attribute_aggregate_version(self, default, elect,
                                          tally_attribute,
                                          return_format=constants.NEST_FORMAT):
        tallies = house.VoteTally.objects.filter(
            booth__seat=self, election=elect).exclude(
            candidate__person__name__iexact="Informal")
        if tallies:
            aggregate = tallies.aggregate(Sum(tally_attribute,
                                              default=default))
            if aggregate:
                if return_format == constants.TRANSACTION_FORMAT:
                    return aggregate.popitem()[1], tallies.query
                return aggregate.popitem()[1]
        return default

    @staticmethod
    def increase_loop_total(tally_attribute, total, vote_tally):
        change = getattr(vote_tally, tally_attribute)
        if change and (change > 0):
            total += change
        else:
            total += getattr(vote_tally, Aggregator.BYPASSES[
                tally_attribute]) or 0
        return total

    @staticmethod
    def set_aggregate(tallies, tally_attribute):
        if getattr(tallies[0], tally_attribute):
            attrib = tally_attribute
        else:
            attrib = Aggregator.BYPASSES[tally_attribute]
        return tallies.aggregate(Sum(attrib, default=0))