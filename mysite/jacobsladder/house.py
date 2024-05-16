from django.db import models
from django.db.models import UniqueConstraint
from . import abstract_models, people, names
from .abstract_models import VoteRecord, Crown, Round, Transfer
from .place import Seat, Booth
from .service import Representation, Contention


class HouseElection(abstract_models.Election):
    BYPASSES = {'primary_votes': 'aec_total'}

    class ElectionType(models.TextChoices):
        REGULAR = "federal", "Regular"
        BY_ELECTION = "by-election", "By-Election"

    election_type = models.CharField(max_length=15,
                                     choices=ElectionType.choices)

    def get_contentions(self, party_abbreviation):
        return [Contention.objects.get(
            election=self, candidate=representation.person.candidate) for
            representation in Representation.objects.filter(
                election=self, party__abbreviation=party_abbreviation)]

    def result_by_place(self, party_set, place_set, places, result,
                        tally_attribute, sum_booths=False):
        representation_set = Representation.objects.filter(election=self,
                                                           party__in=party_set)
        election_result = {}
        if not place_set:
            place_set = Booth.get_set(self, places)
        [self.update_election_result(
            election_result, representation_set, place, tally_attribute,
            sum_booths) for place in place_set]
        result[str(self)] = election_result

    def booths_for_election(self, place_set, places):
        election_result = {}
        if not place_set:
            place_set = Booth.get_set(self, places)
        return election_result, place_set

    def new_dot_node(self, candidate):
        """
        Supply a HouseCandidate.
        Returns a dot node name and text for dot's label attribute for that
        candidate and the party they represented in the election.
        """

        node_name = str(candidate)
        try:
            rep = Representation.objects.get(person=candidate.person,
                                             election=self)
        except Representation.MultipleObjectsReturned:
            rep = Representation.objects.filter(person=candidate.person,
                                                election=self)[0]
        return (node_name, f"{node_name}\n{rep.party.name}"), node_name

    def update_election_result(self, election_result, representation_set,
                               place, tally_attribute, sum_booths=False):
        election_result[str(place)] = self.election_place_result(
            place, representation_set, tally_attribute, sum_booths)

    def results_highest_by_votes(self, election_result, how_many, location,
                                 representation_set, tally_attribute,
                                 sum_booths=False):
        all_parties = self.election_place_result(
            location, representation_set, tally_attribute, sum_booths)
        pairs = list(all_parties.items())
        pairs.sort(key=abstract_models.Election.by_votes)
        election_result[str(location)] = dict(pairs[:how_many])

    def election_place_result(self, place, representation_set, tally_attribute,
                              sum_booths=False):
        result = {}
        total = self.fetch_total(place, sum_booths, tally_attribute)
        [place.update_place_result(
            self, representation, result, total, tally_attribute) for
            representation in representation_set if
            representation.person.name.lower() != 'informal']
        return result

    def highest_by_votes(self, how_many, place_set, places, result,
                         tally_attribute, sum_booths=False):
        election_result, place_set = self.booths_for_election(place_set, places)
        representation_set = Representation.objects.filter(election=self)
        [self.results_highest_by_votes(
            election_result, how_many, location, representation_set,
            tally_attribute, sum_booths) for location in place_set]
        result[str(self)] = election_result

    def fetch_total(self, place, sum_booths, tally_attribute):
        if sum_booths or isinstance(place, Booth):
            return place.total_attribute(self, tally_attribute)
        total = 0
        for vote_tally in VoteTally.objects.filter(
                election=self, bypass=place):
            change = getattr(vote_tally, tally_attribute)
            if change and (change > 0):
                total += change
            else:
                total += getattr(vote_tally, HouseElection.BYPASSES[
                    tally_attribute]) or 0
        return total

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        for election in HouseElection.objects.all().order_by('election_date'):
            return callback(*arguments, election=election, **keyword_arguments)


class HouseCandidate(models.Model):
    person = models.OneToOneField(people.Person, on_delete=models.CASCADE,
                                  related_name='candidate')
    seat = models.ManyToManyField(Seat, through="Contention")

    def __str__(self):
        return str(self.person)


class VoteTally(models.Model):
    class Meta:
        verbose_name_plural = "Vote Tallies"
        constraints = [UniqueConstraint(
            fields=['booth', 'bypass', 'election', 'candidate', ],
            name='booth_bypass_election_candidate')]

    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True)
    bypass = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE)
    tcp_votes = models.IntegerField(null=True, blank=True)
    primary_votes = models.IntegerField(null=True, blank=True)
    absent_votes = models.PositiveIntegerField(default=0)
    provisional_votes = models.PositiveIntegerField(default=0)
    declaration_pre_poll_votes = models.PositiveIntegerField(default=0)
    postal_votes = models.PositiveIntegerField(default=0)
    aec_ordinary = models.PositiveIntegerField(default=0)
    aec_total = models.PositiveIntegerField(default=0)
    aec_swing = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def via_representation(election, party_abbreviation, seat, booth,
                           found_callback=None, not_found_callback=None):
        """
        Supply a HouseElection.
        Supply a party abbreviation as a string.
        Supply a Seat.
        Supply a Booth.
        Returns the VoteTally for the candidate representing that party in
        that booth in that seat in that election.
        """
        representation = Representation.objects.get(
            election=election, party__abbreviation__iexact=party_abbreviation,
            person__candidate__contention__seat=seat,
            person__candidate__contention__election=election
        )
        try:
            vote_tally = VoteTally.objects.get(
                booth=booth, election=election,
                candidate=representation.person.candidate
            )
            if found_callback:
                found_callback(booth, party_abbreviation, vote_tally)
            return vote_tally
        except VoteTally.DoesNotExist:
            if not_found_callback:
                not_found_callback(booth, party_abbreviation)
            return False

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(booth, seat, election):
            return [callback(*arguments, election=election, seat=seat,
                             booth=booth, vote_tally=vote_tally,
                             **keyword_arguments) for vote_tally in
                    VoteTally.objects.filter(booth=booth, election=election)]
        return wrapper

    def __str__(self):
        return str(f"{self.primary_votes or self.aec_total} for "
                   f"{self.candidate} at {self.booth or self.bypass} in "
                   f"{self.election} ({self.pk})")


class PreferenceRound(Crown, Round):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['seat', 'election', 'round_number',],
            name='unique_combination_of_seat_election_round_number')]

    def __str__(self):
        return f"Round {self.round_number} of {self.seat} in {self.election}"


class CandidatePreference(Transfer):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['candidate', 'round', 'seat', 'election'],
            name='unique_combination_of_candidate_round_seat_election')]

    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE,
                                 null=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE,
                             null=True, blank=True)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE,
                                  related_name="target_preference")
    source_candidate = models.ForeignKey(HouseCandidate,
                                         on_delete=models.SET_NULL,
                                         related_name="source_preference",
                                         null=True, blank=True)
    round = models.ForeignKey(PreferenceRound, on_delete=models.CASCADE)
    votes_received = models.IntegerField()
    votes_remaining = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.candidate} in {self.round} ({self.pk})"


class Enrollment(Crown):
    class Meta:
        constraints = [UniqueConstraint(fields=['seat', 'election',],
                                        name='unique_seat_for_election')]

    number_enrolled = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(f"{self.number_enrolled} to vote in "
                   f"{self.seat} in {self.election} ({self.pk})")


class HouseAlliance(names.TrackedName):
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.name} at {self.election} ({self.pk})")


