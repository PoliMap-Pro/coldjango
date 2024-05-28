from django.db import models
#from django.contrib.gis.db import models as gis_models
from django.db.models import UniqueConstraint
from . import model_fields, names, people, house
from .abstract_models import Election, VoteRecord, Contest, Round, \
    Transfer
from .place import Lighthouse, Floor

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


class Geography(models.Model):
    class Meta:
        app_label = 'jacobsladder'

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


class SenateElection(Election):
    class Meta:
        app_label = 'jacobsladder'

    state = models.CharField(max_length=9,
                             choices=model_fields.StateName.choices)


class PartyAlias(names.TrackedName):
    class Meta:
        verbose_name_plural = "Party Aliases"
        app_label = 'jacobsladder'

    party = models.ForeignKey(people.Party, on_delete=models.CASCADE)
    elections = models.ManyToManyField(house.HouseElection, blank=True)


class SenateAlliance(names.TrackedName):
    class Meta:
        app_label = 'jacobsladder'

    election = models.ForeignKey(SenateElection, on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.name} at {self.election} ({self.pk})")


class SenateGroup(models.Model):
    class Meta:
        app_label = 'jacobsladder'

    name = models.CharField(max_length=63, null=True, blank=True)
    abbreviation = models.CharField(max_length=15)
    election = models.ForeignKey(SenateElection, on_delete=models.CASCADE)


class SenateCandidate(models.Model):
    class Meta:
        app_label = 'jacobsladder'

    person = models.OneToOneField(people.Person, on_delete=models.CASCADE)
    group = models.ForeignKey(SenateGroup, on_delete=models.SET_NULL,
                              null=True, blank=True)


class VoteStack(VoteRecord, Contest):
    class Meta:
        app_label = 'jacobsladder'
        constraints = [UniqueConstraint(
            fields=['floor', 'election', 'candidate', ],
            name='floor_election_and_candidate')]

    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, null=True)
    lighthouse = models.ForeignKey(Lighthouse, on_delete=models.CASCADE,
                                   null=True)
    candidate = models.ForeignKey(SenateCandidate, on_delete=models.CASCADE)
    tpp_votes = models.IntegerField(null=True, blank=True)


class Pool(Contest):
    class Meta:
        app_label = 'jacobsladder'
        constraints = [UniqueConstraint(fields=['state', 'election',],
                                        name='pool_state_and_election')]

    formal_papers = models.PositiveIntegerField()
    vacancies = models.PositiveSmallIntegerField()
    quota = models.PositiveIntegerField()


class SenateRound(Round):
    class Meta:
        app_label = 'jacobsladder'

    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)

    def __str__(self):
        return f"Round {self.round_number} for {self.pool.state} in " \
               f"{self.pool.election}"


class SenatePreference(Transfer):
    class Meta:
        app_label = 'jacobsladder'

    election = models.ForeignKey(SenateElection, on_delete=models.CASCADE)
    candidate = models.ForeignKey(SenateCandidate, on_delete=models.CASCADE,
                                  related_name="target_senate")
    source_candidate = models.ForeignKey(SenateCandidate,
                                         on_delete=models.SET_NULL,
                                         related_name="source_senate",
                                         null=True, blank=True)
    round = models.ForeignKey(SenateRound, on_delete=models.CASCADE)
    ballot_position = models.PositiveSmallIntegerField(default=0)
    order_elected = models.PositiveSmallIntegerField(null=True, blank=True)
    papers = models.IntegerField()
    progressive_total = models.PositiveIntegerField()
    transfer_value = models.DecimalField(max_digits=31, decimal_places=29)
    status = models.CharField(max_length=15, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


