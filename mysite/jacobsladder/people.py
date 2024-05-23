import urllib.parse
import re
import urllib.request
import nltk
import collections
import nltk.corpus
from django.db import models
from django.db.models import UniqueConstraint
from . import names, abstract_models, section, constants


class Party(section.Part):
    nltk.download('stopwords')

    class Meta:
        verbose_name_plural = "Parties"
        constraints = [UniqueConstraint(fields=['abbreviation', 'name',],
                                        name='abbreviation_and_name')]

    abbreviation = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=255)
    meta_parties = models.ManyToManyField('MetaParty', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.abbreviation:
            return f"{self.name} ({self.abbreviation})"
        return self.name

    def short_name(self, language='english'):
        frequencies = collections.Counter([
            word for word in
            re.sub(r'[^\w\s_]', '', self.name.lower()).split()
            if word not in nltk.corpus.stopwords.words(language)])
        return urllib.parse.quote_plus(''.join(
            character if character.isalnum() else '_' for character in
            min(frequencies, key=frequencies.get)).strip('-'))

    @classmethod
    def get_set(cls, selector):
        """
        Overrides Part.get_set()
        """
        if selector:
            if isinstance(selector, dict):
                return cls.objects.filter(**selector)
            return selector
        return cls.objects.all()


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


class MetaParty(abstract_models.Club):
    pass