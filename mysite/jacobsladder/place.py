from django.db import models
from django.db.models import UniqueConstraint, Sum
from . import abstract_models, house, geography, service, section, constants
from .format import keep_query


class SeatCode(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['number', 'seat',],
                                        name='number_and_seat')]

    number = models.PositiveIntegerField()
    seat = models.ForeignKey("Seat", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} for {self.seat} ({self.pk})"


class Seat(abstract_models.Beacon):
    name = models.CharField(max_length=63, unique=True)
    elections = models.ManyToManyField("HouseElection", blank=True)

    def ordinary_primary(self, election, party_abbreviation, sum_booths=False):
        """
        Supply a HouseElection.
        Supply a party abbreviation as a string.
        Returns the total ordinary votes for the party in the election.
        """

        representation = house.Representation.objects.get(
            election=election, party__abbreviation__iexact=party_abbreviation,
            person__candidate__contention__seat=self,
            person__candidate__contention__election=election)
        if sum_booths:
            return self.candidate_for(representation.person.candidate, election)
        seat_wide = house.VoteTally.objects.get(
            bypass=self, election=election,
            candidate=representation.person.candidate)
        return seat_wide.aec_ordinary

    def total_attribute(self, elect, tally_attribute, default=0,
                        use_aggregate=True, return_format=constants.NEST_FORMAT):
        if use_aggregate:
            return self.total_attribute_aggregate_version(
                default, elect, tally_attribute, return_format=return_format)
        return self.total_attribute_sum_version(elect, tally_attribute,
                                                default)

    def total_attribute_sum_version(self, elect, tally_attribute, default):
        def return_candidate(election, seat, booth, vote_tally):
            return getattr(vote_tally, tally_attribute) or default if \
                vote_tally.candidate.person.name.lower() != 'informal' else 0

        return sum([votes for booth in Booth.per(house.VoteTally.per(
            return_candidate))(self, elect) for votes in booth])

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

    def candidate_for(self, candidate, elect, tally_attribute='primary_votes',
                      default=0, use_aggregate=True):
        if use_aggregate:
            return self.candidate_for_aggregate_version(candidate, default,
                                                        elect, tally_attribute)
        return self.candidate_for_sum_version(elect, tally_attribute,
                                               default, candidate)

    def candidate_for_sum_version(self, elect, tally_attribute, default,
                                   candidate):
        def attribute_or_zero(election, seat, booth, vote_tally):
            return getattr(vote_tally, tally_attribute) or default if \
                vote_tally.candidate.pk == candidate.pk else 0

        return sum([votes for booth in Booth.per(house.VoteTally.per(
            attribute_or_zero))(self, elect) for votes in booth])

    def candidate_for_aggregate_version(self, candidate, default, elect,
                                        tally_attribute):
        tallies = house.VoteTally.objects.filter(booth__seat=self,
                                                 election=elect,
                                                 candidate__pk=candidate.pk)
        if tallies:
            aggregate = tallies.aggregate(Sum(tally_attribute,
                                              default=default))
            if aggregate:
                return aggregate.popitem()[1]
        return default

    def update_place_result(self, election, representation, result, total,
                            tally_attribute, sum_booths=False,
                            return_format=constants.NEST_FORMAT,
                            election_result=None):
        """
        Most of the execution time gets spent here.
        Checking whether contentions exist each time is the wrong way to
        do this.
        """
















        contentions = service.Contention.objects.filter(
                election=election, seat=self,
                candidate=representation.person.candidate)
        keep_query(return_format, election_result, contentions)
        if contentions.exists():
            self.collect_vote_like(election, election_result, representation,
                                   result, return_format, sum_booths,
                                   tally_attribute, total)

    def add_candidate_source(self, election, last_pref, pref_rounds, trail,
                             trail_index):
        last_pref, previous = self.setup_source(election, last_pref,
                                                pref_rounds, trail_index)
        proximate = last_pref.votes_received - previous.votes_received
        trail.append((last_pref.candidate, proximate,
                      last_pref.round.round_number), )
        return last_pref

    def votes_for_place(self, election, representation, sum_booths,
                        tally_attribute, return_format=constants.NEST_FORMAT,
                        election_result=None):
        if sum_booths:
            return self.candidate_for(representation.person.candidate,
                                      election, tally_attribute)
        query_parameters = {'bypass': self, 'election': election,
                            'candidate': representation.person.candidate}
        seat_wide = house.VoteTally.objects.get(**query_parameters)
        keep_query(return_format, election_result, query_parameters,
                   model=house.VoteTally)
        return seat_wide.aec_ordinary

    def collect_vote_like(self, election, election_result, representation,
                          result, return_format, sum_booths, tally_attribute,
                          total):
        votes = self.votes_for_place(
            election, representation, sum_booths, tally_attribute,
            return_format=return_format, election_result=election_result)
        self.format_results(representation, result, return_format,
                            tally_attribute, total, votes)

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

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(election):
            return [callback(*arguments, election=election, seat=seat,
                             **keyword_arguments) for seat in
                    election.seat_set.all()]
        return wrapper

    @staticmethod
    def total_candidate(election, func):
        Seat.per(Booth.per(house.VoteTally.per(func)))(election)

    @staticmethod
    def get_candidate(election, seat, booth, vote_tally):
        return vote_tally.primary_votes

    def __str__(self):
        return f"{self.__class__.__name__} {self.name} in " \
               f"{self.state}"


class SeatChange(abstract_models.Transition):
    from_seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True,
                                  blank=True, related_name="to_via")
    to_seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True,
                                blank=True, related_name="from_via")


class Booth(geography.Pin):
    class Meta:
        constraints = [UniqueConstraint(fields=['name', 'seat',],
                                        name='name_and_seat')]

    name = models.CharField(max_length=63, null=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    @classmethod
    def get_set(cls, election, selector):
        """
        Overrides section.Part.get_set()
        """

        if selector:
            if isinstance(selector, dict):
                #
                # SLOW VERSION:
                # return [booth for booth in cls.objects.filter(**selector) if
                #         service.Collection.objects.filter(
                #             election=election, booth=booth).exists()]
                #

                selector['collection__election'] = election
                return cls.objects.filter(**selector)
            return selector
        return cls.objects.all()

    def update_place_result(self, election, representation, result, total,
                            tally_attribute, default=0,
                            return_format=constants.NEST_FORMAT,
                            election_result=None):
        candidate = representation.person.candidate
        contentions = service.Contention.objects.filter(
            election=election, seat=self.seat, candidate=candidate)
        keep_query(return_format, election_result, contentions)
        if contentions.exists():
            self.booth_votes(
                candidate, default, election, election_result, representation,
                result, return_format, tally_attribute, total)

    def total_attribute(self, elect, tally_attribute, default=0,
                        return_format=constants.NEST_FORMAT,):
        vote_set = house.VoteTally.objects.filter(booth=self, election=elect)
        result = sum([getattr(vote_tally, tally_attribute) or default for
                     vote_tally in vote_set])
        if return_format == constants.TRANSACTION_FORMAT:
            if vote_set:
                return result, vote_set.query
        return result

    def booth_votes(self, candidate, default, election, election_result,
                    representation, result, return_format, tally_attribute,
                    total):
        query_parameters = {'booth': self, 'election': election,
                            'candidate': candidate}
        keep_query(return_format, election_result, query_parameters,
                   model=house.VoteTally)
        self.format_results(representation, result, return_format,
                            tally_attribute, total, getattr(
                                house.VoteTally.objects.get(**query_parameters),
                                tally_attribute) or default)

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(seat, election):
            return [callback(*arguments, election=election, seat=seat,
                             booth=booth, **keyword_arguments)
                    for booth in [collection.booth for collection in
                                  service.Collection.objects.filter(
                                      booth__seat=seat, election=election)]]
        return wrapper

    def __str__(self):
        if self.name:
            return f"{self.__class__.__name__} {self.name} in " \
                   f"{self.seat}"
        return f"{self.__class__.__name__} #{self.pk}"


class BoothChange(abstract_models.Transition):
    from_booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True,
                                   blank=True, related_name="to_via")
    to_booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True,
                                 blank=True, related_name="from_via")


class BoothCode(models.Model):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['number', 'booth',],
            name='unique_combination_of_number_and_booth')]

    number = models.PositiveIntegerField()
    booth = models.ForeignKey("Booth", on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.number} for {self.booth} ({self.pk})")


class LighthouseCode(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['number', 'lighthouse',],
                                        name='number_and_lighthouse')]

    number = models.PositiveIntegerField()
    lighthouse = models.ForeignKey("Lighthouse", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} for {self.lighthouse} ({self.pk})"


class Lighthouse(abstract_models.Beacon):
    name = models.CharField(max_length=63, unique=True)
    elections = models.ManyToManyField("SenateElection", blank=True)


class FloorCode(models.Model):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['number', 'floor',],
            name='unique_combination_of_number_and_floor')]

    number = models.PositiveIntegerField()
    floor = models.ForeignKey("Floor", on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.number} for {self.floor} ({self.pk})")


class Floor(geography.Pin):
    class Meta:
        constraints = [UniqueConstraint(fields=['name', 'lighthouse',],
                                        name='name_and_lighthouse')]

    name = models.CharField(max_length=63, null=True, blank=True)
    lighthouse = models.ForeignKey(Lighthouse, on_delete=models.CASCADE)