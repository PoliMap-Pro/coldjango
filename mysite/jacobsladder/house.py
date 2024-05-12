from django.db import models
from django.db.models import UniqueConstraint
from . import abstract_models, people


class HouseElection(abstract_models.Election):
    class ElectionType(models.TextChoices):
        REGULAR = "federal", "Regular"
        EQUESTRIAN = "equestrian", "Equestrian"

    election_type = models.CharField(max_length=15,
                                     choices=ElectionType.choices)

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

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        for election in HouseElection.objects.all().order_by('election_date'):
            return callback(*arguments, election=election, **keyword_arguments)


class Representation(models.Model):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['person', 'party', 'election'],
            name='representation_person_party_election')]

    person = models.ForeignKey(people.Person, on_delete=models.CASCADE)
    party = models.ForeignKey(people.Party, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)