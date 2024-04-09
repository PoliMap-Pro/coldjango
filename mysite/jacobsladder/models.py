from django.db import models
#from django.contrib.gis.db import models as gis_models


class StateName(models.TextChoices):
    ACT = "act", "Australian Capital Territory"
    NSW = "nsw", "New South Wales"
    NT = "nt", "Northern Territory"
    QLD = "qld", "Queensland"
    SA = "sa", "South Australia"
    TAS = "tasmania", "Tasmania"
    VIC = "victoria", "Victoria"
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


class HouseElection(Election):
    class ElectionType(models.TextChoices):
        REGULAR = "federal", "Regular"
        EQUESTRIAN = "equestrian", "Equestrian"

    election_type = models.CharField(max_length=15,
                                     choices=ElectionType.choices)

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        for election in HouseElection.objects.all().order_by('election_date'):
            callback(*arguments, election=election, **keyword_arguments)


class SenateElection(Election):
    state = models.CharField(max_length=9, choices=StateName.choices)


class Seat(models.Model):
    name = models.CharField(max_length=63, unique=True)
    state = models.CharField(max_length=9, choices=StateName.choices)
    elections = models.ManyToManyField(HouseElection, blank=True)
    location = models.OneToOneField(Geography, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(election):
            for seat in election.seat_set.all():
                callback(*arguments, election=election, seat=seat,
                         **keyword_arguments)
        return wrapper


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


class Booth(models.Model):
    name = models.CharField(max_length=63, null=True, blank=True)
    seats = models.ManyToManyField(HouseElection, blank=True,
                                   through="Collection")
    location = models.OneToOneField(Geography, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(seat, election):
            for collection in Collection.objects.filter(
                    seat=seat, election=election):
                callback(*arguments, election=election, seat=seat,
                         booth=collection.booth, **keyword_arguments)
        return wrapper


class Collection(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)


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


class Person(models.Model):
    name = models.CharField(max_length=63)
    party = models.ManyToManyField(Party, through="Representation")
    created = models.DateTimeField(auto_now_add=True)


class Representation(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)


class HouseCandidate(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    seat = models.ManyToManyField(Seat, through="Contention")


class Contention(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)


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

    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE)
    primary_votes = models.IntegerField()
    tcp_votes = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(booth, seat, election):
            for vote_tally in VoteTally.objects.filter(
                    booth=booth, election=election):
                callback(*arguments, election=election, seat=seat, booth=booth,
                         vote_tally=vote_tally, **keyword_arguments)
        return wrapper




class PreferenceRound(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)
    round_number = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)


class CandidatePreference(models.Model):
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE)
    round = models.ForeignKey(PreferenceRound, on_delete=models.CASCADE)
    votes_received = models.IntegerField()
    votes_transferred = models.IntegerField()
    votes_remaining = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)


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



