from django.db import models
from . import geography, model_fields, names, section


class Election(section.Part):
    class Meta:
        abstract = True

    election_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.__class__.__name__} in " \
               f"{self.election_date.year} ({self.pk})"


class Beacon(geography.Pin):
    class Meta:
        abstract = True

    state = models.CharField(max_length=9,
                             choices=model_fields.StateName.choices)


class Crown(models.Model):
    class Meta:
        abstract = True

    seat = models.ForeignKey('Seat', on_delete=models.CASCADE)
    election = models.ForeignKey('HouseElection', on_delete=models.CASCADE)


class Transfer(models.Model):
    class Meta:
        abstract = True

    votes_transferred = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)


class BallotEntry(Crown):
    class Meta:
        abstract = True

    ballot_position = models.PositiveSmallIntegerField(default=0)


class Club(names.TrackedName):
    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Transition(models.Model):
    class Meta:
        abstract = True

    reason = models.CharField(max_length=127)
    date_of_change = models.DateField()
    created = models.DateTimeField(auto_now_add=True)


class VoteRecord(models.Model):
    class Meta:
        abstract = True

    primary_votes = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)


class Contest(models.Model):
    class Meta:
        abstract = True

    state = models.CharField(max_length=9,
                             choices=model_fields.StateName.choices)
    election = models.ForeignKey("SenateElection", on_delete=models.CASCADE)


class Round(models.Model):
    class Meta:
        abstract = True

    round_number = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
