from django.db import models
#from django.contrib.gis.db import models as gis_models
from django.db.models import UniqueConstraint

""" 
HouseElection.per, Seat.per, Booth.per and VoteTally.per
call the function you supply once for each house election, 
seat, both or vote tally. 
For example,

    (1) HouseElection.per(lambda election: print(election)) prints something like,
    HouseElection on 2010-01-01
    HouseElection on 2013-01-01

    (2) Seat.per(lam)(el_2020) prints something like,
    HouseElection on 2010-01-01 Seat Frank in victoria
    HouseElection on 2010-01-01 Seat Yossarian in victoria
    
    (3) el_2020.per(Seat.per(lam)) prints something like
    HouseElection on 2010-01-01 Seat Frank in victoria
    HouseElection on 2010-01-01 Seat Yossarian in victoria
    HouseElection on 2013-01-01 Seat Frank in victoria
    HouseElection on 2013-01-01 Seat Yossarian in victoria
        
    (4) Booth.per(lam2)(s, el_2020) prints something like,
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #22
    
    (5) Seat.per(Booth.per(lam2))(el_2020) prints something like,
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #22
    
    (6) HouseElection.per(Seat.per(Booth.per(lam2))) prints something like,
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #22
    HouseElection on 2013-01-01 Seat Frank in victoria Booth #18
    HouseElection on 2013-01-01 Seat Yossarian in victoria Booth #20
    HouseElection on 2013-01-01 Seat Yossarian in victoria Booth #22

    (7) VoteTally.per(lam3)(b, s, el_2020) prints something like,
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #21 VoteTally object (13)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #21 VoteTally object (14)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #21 VoteTally object (17)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #21 VoteTally object (19)

    (8) Booth.per(VoteTally.per(lam3))(s, el_2020) prints something like,
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (22)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (23)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (28)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #22 VoteTally object (32)

    (9) Seat.per(Booth.per(VoteTally.per(lam3)))(el_2020) prints something like,
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18 VoteTally object (10)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18 VoteTally object (11)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18 VoteTally object (16)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18 VoteTally object (18)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21 VoteTally object (13)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21 VoteTally object (14)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21 VoteTally object (17)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21 VoteTally object (19)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (22)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (23)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (28)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #22 VoteTally object (32)

    (10) HouseElection.per(Seat.per(Booth.per(VoteTally.per(lam3)))) prints something like,
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18 VoteTally object (10)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18 VoteTally object (11)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18 VoteTally object (16)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #18 VoteTally object (18)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21 VoteTally object (13)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21 VoteTally object (14)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21 VoteTally object (17)
    HouseElection on 2010-01-01 Seat Frank in victoria Booth #21 VoteTally object (19)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (22)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (23)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #19 VoteTally object (28)
    HouseElection on 2010-01-01 Seat Yossarian in victoria Booth #22 VoteTally object (32)
    HouseElection on 2013-01-01 Seat Frank in victoria Booth #18 VoteTally object (12)
    HouseElection on 2013-01-01 Seat Frank in victoria Booth #18 VoteTally object (20)
    HouseElection on 2013-01-01 Seat Frank in victoria Booth #18 VoteTally object (21)
    HouseElection on 2013-01-01 Seat Yossarian in victoria Booth #20 VoteTally object (24)
    HouseElection on 2013-01-01 Seat Yossarian in victoria Booth #20 VoteTally object (25)
    HouseElection on 2013-01-01 Seat Yossarian in victoria Booth #20 VoteTally object (31)
    HouseElection on 2013-01-01 Seat Yossarian in victoria Booth #22 VoteTally object (26)
    HouseElection on 2013-01-01 Seat Yossarian in victoria Booth #22 VoteTally object (27)
    HouseElection on 2013-01-01 Seat Yossarian in victoria Booth #22 VoteTally object (33)

where, 
    b = Booth.objects.get(pk=21)
    s = Seat.objects.get(name="Yossarian")
    el_2020 = HouseElection.objects.get(election_date=datetime(
    year=2010, month=1, day=1))
    lam = lambda election, seat: print(election, seat)
    lam2 = lambda election, seat, booth: print(election, seat, booth)
    lam3 = lambda election, seat, booth, vote_tally: print(election, seat, booth, vote_tally)    
 """


class StateName(models.TextChoices):
    ACT = "act", "Australian Capital Territory"
    NSW = "nsw", "New South Wales"
    NT = "nt", "Northern Territory"
    QLD = "qld", "Queensland"
    SA = "sa", "South Australia"
    TAS = "tas", "Tasmania"
    VIC = "vic", "Victoria"
    WA = "wa", "Western Australia"


class Geography(models.Model):
    #multi_polygon = gis_models.MultiPolygonField()
    un = models.IntegerField("United Nations Code")
    area = models.IntegerField()
    region = models.IntegerField("Region Code")
    subregion = models.IntegerField("Sub-Region Code")
    pop2005 = models.IntegerField("Population 2005")
    name = models.CharField(max_length=50)
    fips = models.CharField("FIPS Code", max_length=2, null=True)
    iso2 = models.CharField("2 Digit ISO", max_length=2)
    iso3 = models.CharField("3 Digit ISO", max_length=3)
    lat = models.FloatField()
    lon = models.FloatField()


class Election(models.Model):
    class Meta:
        abstract = True

    election_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.__class__.__name__} on {self.election_date} ({self.pk})"


class HouseElection(Election):
    class ElectionType(models.TextChoices):
        REGULAR = "federal", "Regular"
        EQUESTRIAN = "equestrian", "Equestrian"

    election_type = models.CharField(max_length=15,
                                     choices=ElectionType.choices)

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        for election in HouseElection.objects.all().order_by('election_date'):
            return callback(*arguments, election=election, **keyword_arguments)


class SenateElection(Election):
    state = models.CharField(max_length=9, choices=StateName.choices)


class SeatCode(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['number', 'seat',],
                                        name='number_and_seat')]

    number = models.PositiveIntegerField()
    seat = models.ForeignKey("Seat", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} for {self.seat} ({self.pk})"


class Seat(models.Model):
    name = models.CharField(max_length=63, unique=True)
    state = models.CharField(max_length=9, choices=StateName.choices)
    elections = models.ManyToManyField(HouseElection, blank=True)
    location = models.OneToOneField(Geography, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def total_primary_votes(self, elect):
        def return_candidate(election, seat, booth, vote_tally):
            return vote_tally.primary_votes
        return sum([votes for booth in Booth.per(VoteTally.per(
            return_candidate))(self, elect) for votes in booth])

    def candidate_for(self, candidate, elect):
        def primary_votes(election, seat, booth, vote_tally):
            return vote_tally.primary_votes if vote_tally.candidate.pk == \
                                               candidate.pk else 0
        return sum([votes for booth in Booth.per(VoteTally.per(primary_votes))(
            self, elect) for votes in booth])

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(election):
            return [callback(*arguments, election=election, seat=seat,
                             **keyword_arguments) for seat in
                    election.seat_set.all()]
        return wrapper

    @staticmethod
    def total_candidate(election, func):
        Seat.per(Booth.per(VoteTally.per(func)))(election)

    @staticmethod
    def get_candidate(election, seat, booth, vote_tally):
        return vote_tally.primary_votes

    def __str__(self):
        return f"{self.__class__.__name__} {self.name} in " \
               f"{self.state} ({self.pk})"


class Enrollment(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['seat', 'election',],
                                        name='unique_seat_for_election')]

    number_enrolled = models.PositiveIntegerField(default=0)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection,
                                 on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.number_enrolled} to vote in "
                   f"{self.seat} in {self.election} ({self.pk})")


class Transition(models.Model):
    class Meta:
        abstract = True

    reason = models.CharField(max_length=127)
    date_of_change = models.DateField()
    created = models.DateTimeField(auto_now_add=True)


class SeatChange(Transition):
    from_seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True,
                                  blank=True, related_name="to_via")
    to_seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True,
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


class Booth(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['name', 'seat',],
                                        name='name_and_seat')]

    name = models.CharField(max_length=63, null=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    location = models.OneToOneField(Geography, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(seat, election):
            return [callback(*arguments, election=election, seat=seat,
                             booth=booth, **keyword_arguments)
                    for booth in Booth.objects.filter(
                    seat=seat)]
        return wrapper

    def __str__(self):
        if self.name:
            return f"{self.__class__.__name__} {self.name} ({self.pk})"
        return f"{self.__class__.__name__} #{self.pk}"


class Collection(models.Model):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['booth', 'election',],
            name='unique_combination_of_booth_election')]

    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.booth} in {self.election} ({self.pk})")


class BoothChange(Transition):
    from_booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True,
                                   blank=True, related_name="to_via")
    to_booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True,
                                 blank=True, related_name="from_via")


class Party(models.Model):
    class Meta:
        verbose_name_plural = "Parties"

    name = models.CharField(max_length=63)
    abbreviation = models.CharField(max_length=15, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


class PartyAlias(models.Model):
    class Meta:
        verbose_name_plural = "Party Aliases"

    name = models.CharField(max_length=63)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    elections = models.ManyToManyField(HouseElection, blank=True)
    created = models.DateTimeField(auto_now_add=True)


class PersonCode(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['number', 'person',],
                                        name='number_and_person')]

    number = models.PositiveIntegerField()
    person = models.ForeignKey("Person", on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.number} in {self.person} ({self.pk})")


class Person(models.Model):
    name = models.CharField(max_length=31)  # surname
    other_names = models.CharField(max_length=63, null=True, blank=True)
    party = models.ManyToManyField(Party, through="Representation")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.other_names:
            return f"{str(self.other_names).title()} " \
                   f"{str(self.name).title()} ({self.pk})"
        return str(self.name).title()


class Representation(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['person', 'party', 'election'],
                                        name='representation_person_party_election')]

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)


class HouseCandidate(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE,
                                  related_name='candidate')
    seat = models.ManyToManyField(Seat, through="Contention")

    def __str__(self):
        return str(self.person)


class Contention(models.Model):
    constraints = [UniqueConstraint(
        fields=['seat', 'candidate', 'election', ],
        name='unique_seat_candidate_election')]

    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)
    ballot_position = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(f"{self.candidate} for {self.seat} "
                   f"in {self.election} ({self.pk})")


class SenateGroup(models.Model):
    name = models.CharField(max_length=63)
    abbreviation = models.CharField(max_length=15, null=True, blank=True)
    election = models.ForeignKey(SenateElection, on_delete=models.CASCADE)


class SenateCandidate(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(SenateGroup, on_delete=models.SET_NULL,
                              null=True, blank=True)


class VoteTally(models.Model):
    class Meta:
        verbose_name_plural = "Vote Tallies"
        constraints = [UniqueConstraint(
            fields=['booth', 'election', 'candidate', ],
            name='unique_combination_of_booth_election_and_candidate')]

    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE)
    primary_votes = models.IntegerField()
    tcp_votes = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(booth, seat, election):
            return [callback(*arguments, election=election, seat=seat,
                             booth=booth, vote_tally=vote_tally,
                             **keyword_arguments) for vote_tally in
                    VoteTally.objects.filter(booth=booth, election=election)]
        return wrapper

    def __str__(self):
        return str(f"{self.primary_votes} for {self.candidate} "
                   f"at {self.booth} in {self.election} ({self.pk})")


class PreferenceRound(models.Model):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['seat', 'election', 'round_number',],
            name='unique_combination_of_seat_election_round_number')]

    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)
    round_number = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Round {self.round_number} of {self.seat} in {self.election}"


class CandidatePreference(models.Model):
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
                                         on_delete=models.CASCADE,
                                         related_name="source_preference",
                                         null=True, blank=True)
    round = models.ForeignKey(PreferenceRound, on_delete=models.CASCADE)
    votes_received = models.IntegerField()
    votes_transferred = models.IntegerField()
    votes_remaining = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate} in {self.round} ({self.pk})"


# not using VoteTransfer and VoteDistribution
class VoteTransfer(models.Model):
    source_candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE,
                                         related_name="to_via")
    target_candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE,
                                         related_name="from_via")
    round = models.ForeignKey(PreferenceRound, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class VoteDistribution(models.Model):
    election = models.ForeignKey(SenateElection, on_delete=models.CASCADE)
    round_number = models.IntegerField()
    candidate = models.ForeignKey(SenateCandidate, on_delete=models.CASCADE)
    source_tally = models.ForeignKey(VoteTally, on_delete=models.CASCADE)
    vote_count_change = models.IntegerField()
    reason = models.CharField(max_length=127)
    created = models.DateTimeField(auto_now_add=True)



