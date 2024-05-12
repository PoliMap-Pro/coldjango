from django.db import models
from django.db.models import UniqueConstraint
from . import names


class Party(models.Model):
    class Meta:
        verbose_name_plural = "Parties"
        constraints = [UniqueConstraint(fields=['abbreviation', 'name',],
                                        name='abbreviation_and_name')]

    abbreviation = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=255)
    meta_party = models.ForeignKey('MetaParty', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)


class PersonCode(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['number', 'person',],
                                        name='number_and_person')]

    number = models.PositiveIntegerField()
    person = models.ForeignKey("Person", on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.number} in {self.person} ({self.pk})")


class Person(names.TrackedName):
    other_names = models.CharField(max_length=63, null=True, blank=True)
    party = models.ManyToManyField(Party, through="Representation")

    def __str__(self):
        if self.other_names:
            return f"{str(self.other_names).title()} " \
                   f"{str(self.name).title()} ({self.pk})"
        return str(self.name).title()