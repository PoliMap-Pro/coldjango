from django.db import models
from django.db.models import UniqueConstraint
from . import abstract_models, house, geography, service


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

    def ordinary_primary(self, election, party_abbreviation):
        """
        Supply a HouseElection.
        Supply a party abbreviation as a string.
        Returns the total ordinary votes for the party in the election.
        """
        representation = house.Representation.objects.get(
            election=election, party__abbreviation__iexact=party_abbreviation,
            person__candidate__contention__seat=self,
            person__candidate__contention__election=election)
        return self.candidate_for(representation.person.candidate, election)

    def total_primary_votes(self, elect):
        def return_candidate(election, seat, booth, vote_tally):
            return vote_tally.primary_votes
        return sum([votes for booth in Booth.per(house.VoteTally.per(
            return_candidate))(self, elect) for votes in booth])

    def candidate_for(self, candidate, elect):
        def primary_votes(election, seat, booth, vote_tally):
            return vote_tally.primary_votes if vote_tally.candidate.pk == \
                                               candidate.pk else 0
        return sum([votes for booth in Booth.per(house.VoteTally.per(primary_votes))(
            self, elect) for votes in booth])

    def add_candidate_source(self, election, last_pref, pref_rounds, trail,
                             trail_index):
        last_pref, previous = self.setup_source(election, last_pref,
                                                pref_rounds, trail_index)
        proximate = last_pref.votes_received - previous.votes_received
        trail.append((last_pref.candidate, proximate,
                      last_pref.round.round_number), )
        return last_pref

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
               f"{self.state} ({self.pk})"


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
            return f"{self.__class__.__name__} {self.name} ({self.pk})"
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