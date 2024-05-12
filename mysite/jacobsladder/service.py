from django.db import models
from django.db.models import UniqueConstraint
from . import abstract_models


class Representation(models.Model):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['person', 'party', 'election'],
            name='representation_person_party_election')]

    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    party = models.ForeignKey("Party", on_delete=models.CASCADE)
    election = models.ForeignKey("HouseElection", on_delete=models.CASCADE)


class Collection(models.Model):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['booth', 'election',],
            name='unique_combination_of_booth_election')]

    booth = models.ForeignKey("Booth", on_delete=models.CASCADE)
    election = models.ForeignKey("HouseElection", on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.booth} in {self.election} ({self.pk})")


class Contention(abstract_models.BallotEntry):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['seat', 'candidate', 'election', ],
            name='unique_seat_candidate_election')]

    candidate = models.ForeignKey("HouseCandidate", on_delete=models.CASCADE)
    alliance = models.ForeignKey("HouseAlliance", null=True, blank=True,
                                 on_delete=models.SET_NULL)

    def __str__(self):
        return str(f"{self.candidate} for {self.seat} "
                   f"in {self.election} ({self.pk})")


class Selection(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['person', 'election'],
                                        name='selection_person_election')]
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    party = models.ForeignKey("Party", on_delete=models.SET_NULL,
                              null=True, blank=True)
    election = models.ForeignKey("SenateElection", on_delete=models.CASCADE)


class Stand(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['candidate', 'election', ],
                                        name='candidate_election')]

    candidate = models.ForeignKey('SenateCandidate', on_delete=models.CASCADE)
    election = models.ForeignKey('SenateElection', on_delete=models.CASCADE)
    alliance = models.ForeignKey("SenateAlliance", null=True, blank=True,
                                 on_delete=models.SET_NULL)

    ballot_position = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(f"{self.candidate} in {self.election} ({self.pk})")