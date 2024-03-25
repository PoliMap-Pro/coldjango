from django.db import models
#from django.contrib.gis.db import models as gis_models

"""
Table elections {
  ElectionID int [pk]
  ElectionDate date
  ElectionType varchar
}

Table seats {
  SeatID int [pk]
  SeatName varchar
  State varchar
  ElectionID int [ref: > elections.ElectionID]
  previous int [ref: > SeatID]
  Geometry geometry
}

Table booths {
  BoothID int [pk]
  BoothName varchar
  SeatID int [ref: > seats.SeatID]
  ElectionID int [ref: > elections.ElectionID]
  Location geometry
}

Table votes {
  VoteID int [pk]
  BoothID int [ref: > booths.BoothID]
  SeatID int [ref: > seats.SeatID]
  ElectionID int [ref: > elections.ElectionID]
  PrimaryVotes int
  TCPVotes int
  CandidateID int [ref: > candidates.CandidateID]
}

Table candidates {
  CandidateID int [pk]
  Name varchar
  PartyID int [ref: > parties.PartyID]
}

Table parties {
  PartyID int [pk]
  PartyName varchar
  Abbreviation varchar
}

Table party_aliases {
  AliasID int [pk]
  PartyID int [ref: > parties.PartyID]
  Alias varchar
  ElectionID int [ref: > elections.ElectionID]
}

Table seat_history {
  HistoryID int [pk]
  PreviousSeatID int [ref: > seats.SeatID]
  CurrentSeatID int [ref: > seats.SeatID]
  ReasonForChange text
}

Table booth_history {
  HistoryID int [pk]
  PreviousBoothID int [ref: > booths.BoothID]
  CurrentBoothID int [ref: > booths.BoothID]
  ReasonForChange text
}

Table preference_rounds {
  RoundID int [pk]
  SeatID int [ref: > seats.SeatID]
  ElectionID int [ref: > elections.ElectionID]
  RoundNumber int
}

Table candidate_preferences {
  PreferenceID int [pk]
  RoundID int [ref: > preference_rounds.RoundID]
  CandidateID int [ref: > candidates.CandidateID]
  VotesReceived int
  VotesTransferred int
  RemainingVotes int
}

Table vote_transfers {
  TransferID int [pk]
  SourceCandidateID int [ref: > candidates.CandidateID]
  TargetCandidateID int [ref: > candidates.CandidateID]
  RoundID int [ref: > preference_rounds.RoundID]
  VoteCount int
}

// Senate now!
Table senate_elections {
  ElectionID int [pk]
  ElectionDate date
  State varchar
}

Table senate_groups {
  GroupID int [pk]
  ElectionID int [ref: > senate_elections.ElectionID]
  GroupName varchar
  GroupAbbreviation varchar
  State varchar
}

Table senate_candidates {
  CandidateID int [pk]
  ElectionID int [ref: > senate_elections.ElectionID]
  Name varchar
  GroupID int [ref: > senate_groups.GroupID]
}

Table senate_votes {
  VoteID int [pk]
  ElectionID int [ref: > senate_elections.ElectionID]
  Type varchar // 'above' or 'below'
  Preferences text // Consider a more structured approach for large-scale implementations
}

Table vote_distribution {
  DistributionID int [pk]
  ElectionID int [ref: > senate_elections.ElectionID]
  RoundNumber int
  AffectedCandidateID int [ref: > senate_candidates.CandidateID]
  SourceVoteID int [ref: > senate_votes.VoteID]
  VoteCountChange int
  Reason varchar
}
"""


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


class SenateElection(Election):
    state = models.CharField(max_length=9, choices=StateName.choices)


class Seat(models.Model):
    name = models.CharField(max_length=63)
    state = models.CharField(max_length=9, choices=StateName.choices)
    elections = models.ManyToManyField(HouseElection, blank=True)
    location = models.OneToOneField(Geography, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


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
    seats = models.ManyToManyField(HouseElection, blank=True, through="Collection")
    location = models.OneToOneField(Geography, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


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

    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE)
    primary_votes = models.IntegerField()
    tcp_votes = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)


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



