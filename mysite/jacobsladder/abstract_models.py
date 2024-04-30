from django.db import models
from .model_fields import StateName


class Election(models.Model):
    class Meta:
        abstract = True

    election_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.__class__.__name__} on {self.election_date} ({self.pk})"


class Pin(models.Model):
    class Meta:
        abstract = True

    location = models.OneToOneField('Geography', on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


class Beacon(Pin):
    class Meta:
        abstract = True

    state = models.CharField(max_length=9, choices=StateName.choices)


class Crown(models.Model):
    class Meta:
        abstract = True

    seat = models.ForeignKey('Seat', on_delete=models.CASCADE)
    election = models.ForeignKey('HouseElection',
                                 on_delete=models.CASCADE)


class BallotEntry(Crown):
    class Meta:
        abstract = True

    ballot_position = models.PositiveSmallIntegerField(default=0)


class TrackedName(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=63)
    created = models.DateTimeField(auto_now_add=True)


class Transition(models.Model):
    class Meta:
        abstract = True

    reason = models.CharField(max_length=127)
    date_of_change = models.DateField()
    created = models.DateTimeField(auto_now_add=True)