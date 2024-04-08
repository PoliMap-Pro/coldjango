from datetime import datetime

from django.core.management.base import BaseCommand


from ... import models


class Command(BaseCommand):
    help = 'Add votes'

    def handle(self, *arguments, **keywordarguments):
        seat1 = models.Seat.objects.get(name="Frank")
        seat2 = models.Seat.objects.get(name="Yossarian")
        twenty_ten = datetime(year=2010, month=1, day=1)
        twenty_thirteen = datetime(year=2013, month=1, day=1)
        house_election_2010 = models.HouseElection.objects.get(
            election_date=twenty_ten)
        house_election_2013 = models.HouseElection.objects.get(
            election_date=twenty_thirteen)
        guy = models.Person.objects.get(name="Party Hack")
        other_guy = models.Person.objects.get(name="Dangerous Idealogue")
        third_guy = models.Person.objects.get(name="Narcissist")
        fourth_guy = models.Person.objects.get(name="Crypto-Fascist")
        fifth_guy = models.Person.objects.get(name="Bored Billionaire")
        sixth_guy = models.Person.objects.get(name="Scandal Magnet")
        seventh_guy = models.Person(name="Outmaneuvered Idealist")
        seventh_guy.save()
        eighth_guy = models.Person(name="Rural Blowhard")
        eighth_guy.save()
        hack = models.HouseCandidate.objects.get(person=guy)
        imp = models.HouseCandidate.objects.get(person=other_guy)
        noise = models.HouseCandidate.objects.get(person=third_guy)
        fourth = models.HouseCandidate.objects.get(person=fourth_guy)
        fifth = models.HouseCandidate.objects.get(person=fifth_guy)
        sixth = models.HouseCandidate.objects.get(person=sixth_guy)
        seventh = models.HouseCandidate(person=seventh_guy)
        seventh.save()
        eighth = models.HouseCandidate(person=eighth_guy)
        eighth.save()
        contention_a = models.Contention(candidate=seventh, seat=seat1,
                                         election=house_election_2010)
        contention_a.save()
        contention_b = models.Contention(candidate=seventh, seat=seat1,
                                         election=house_election_2013)
        contention_b.save()
        contention_c = models.Contention(candidate=eighth, seat=seat2,
                                         election=house_election_2010)
        contention_c.save()
        contention_d = models.Contention(candidate=eighth, seat=seat2,
                                         election=house_election_2013)
        contention_d.save()
        booth_frank_1 = models.Booth.objects.get(id=18)
        booth_frank_2 = models.Booth.objects.get(id=21)
        booth_yossarian_1 = models.Booth.objects.get(id=19)
        booth_yossarian_2 = models.Booth.objects.get(id=20)
        booth_yossarian_3 = models.Booth()
        booth_yossarian_3.save()
        collection_yossarian_3_2010 = models.Collection(
            booth=booth_yossarian_3, seat=seat2, election=house_election_2010)
        collection_yossarian_3_2010.save()
        collection_yossarian_3_2013 = models.Collection(
            booth=booth_yossarian_3, seat=seat2, election=house_election_2013)
        collection_yossarian_3_2013.save()
        tally_frank_1_hack_2010 = models.VoteTally(
            booth=booth_frank_1, election=house_election_2010,
            candidate=hack, primary_votes=3424, tcp_votes=5006)
        tally_frank_1_hack_2010.save()
        tally_frank_1_seventh_2010 = models.VoteTally(
            booth=booth_frank_1, election=house_election_2010,
            candidate=seventh, primary_votes=424, tcp_votes=0)
        tally_frank_1_seventh_2010.save()
        tally_frank_1_seventh_2013 = models.VoteTally(
            booth=booth_frank_1, election=house_election_2013,
            candidate=seventh, primary_votes=848, tcp_votes=0)
        tally_frank_1_seventh_2013.save()
        tally_frank_2_hack_2010 = models.VoteTally(
            booth=booth_frank_2,  election=house_election_2010,
            candidate=hack, primary_votes=6848, tcp_votes=7006)
        tally_frank_2_hack_2010.save()
        tally_frank_2_seventh_2010 = models.VoteTally(
            booth=booth_frank_2,  election=house_election_2010,
            candidate=seventh, primary_votes=848, tcp_votes=0)
        tally_frank_2_seventh_2010.save()
        tally_frank_2_seventh_2013 = models.VoteTally(
            booth=booth_frank_2,  election=house_election_2013,
            candidate=seventh, primary_votes=383, tcp_votes=0)
        tally_frank_2_seventh_2013.save()
        tally_frank_1_imp_2010 = models.VoteTally(
            booth=booth_frank_1, election=house_election_2010,
            candidate=imp, primary_votes=123, tcp_votes=3232)
        tally_frank_1_imp_2010.save()
        tally_frank_2_imp_2010 = models.VoteTally(
            booth=booth_frank_2, election=house_election_2010,
            candidate=imp, primary_votes=246, tcp_votes=6464)
        tally_frank_2_imp_2010.save()
        tally_frank_1_noise_2010 = models.VoteTally(
            booth=booth_frank_1, election=house_election_2010,
            candidate=noise, primary_votes=45, tcp_votes=0)
        tally_frank_1_noise_2010.save()
        tally_frank_2_noise_2010 = models.VoteTally(
            booth=booth_frank_2, election=house_election_2010,
            candidate=noise, primary_votes=80, tcp_votes=0)
        tally_frank_2_noise_2010.save()
        tally_frank_1_sixth_2013 = models.VoteTally(
            booth=booth_frank_1, election=house_election_2013,
            candidate=sixth, primary_votes=2345, tcp_votes=4564)
        tally_frank_1_sixth_2013.save()
        tally_frank_1_imp_2013 = models.VoteTally(
            booth=booth_frank_1, election=house_election_2013,
            candidate=imp, primary_votes=3453, tcp_votes=6356)
        tally_frank_1_imp_2013.save()
        tally_yossarian_1_fourth_2010 = models.VoteTally(
            booth=booth_yossarian_1, election=house_election_2010 ,
            candidate=fourth, primary_votes=456, tcp_votes=1456)
        tally_yossarian_1_fourth_2010.save()
        tally_yossarian_1_fifth_2010 = models.VoteTally(
            booth=booth_yossarian_1, election=house_election_2010,
            candidate=fifth, primary_votes=77, tcp_votes=77)
        tally_yossarian_1_fifth_2010.save()
        tally_yossarian_2_noise_2013 = models.VoteTally(
            booth=booth_yossarian_2, election=house_election_2013,
            candidate=noise, primary_votes=1564, tcp_votes=2075)
        tally_yossarian_2_noise_2013.save()
        tally_yossarian_2_fifth_2013 = models.VoteTally(
            booth=booth_yossarian_2, election=house_election_2013,
            candidate=fifth, primary_votes=64, tcp_votes=64)
        tally_yossarian_2_fifth_2013.save()
        tally_yossarian_3_noise_2013 = models.VoteTally(
            booth=booth_yossarian_3, election=house_election_2013,
            candidate=noise, primary_votes=2018, tcp_votes=4020)
        tally_yossarian_3_noise_2013.save()
        tally_yossarian_3_fifth_2013 = models.VoteTally(
            booth=booth_yossarian_3, election=house_election_2013,
            candidate=fifth, primary_votes=18, tcp_votes=18)
        tally_yossarian_3_fifth_2013.save()

        tally_yossarian_1_eighth_2010 = models.VoteTally(
            booth=booth_yossarian_1, election=house_election_2010,
            candidate=eighth, primary_votes=162, tcp_votes=0)
        tally_yossarian_1_eighth_2010.save()
        tally_yossarian_1_eighth_2013 = models.VoteTally(
            booth=booth_yossarian_1, election=house_election_2013,
            candidate=eighth, primary_votes=427, tcp_votes=0)
        tally_yossarian_1_eighth_2013.save()
        tally_yossarian_2_eighth_2010 = models.VoteTally(
            booth=booth_yossarian_2, election=house_election_2010,
            candidate=eighth, primary_votes=686, tcp_votes=0)
        tally_yossarian_2_eighth_2010.save()
        tally_yossarian_2_eighth_2013 = models.VoteTally(
            booth=booth_yossarian_2, election=house_election_2013,
            candidate=eighth, primary_votes=261, tcp_votes=0)
        tally_yossarian_2_eighth_2013.save()
        tally_yossarian_3_eighth_2010 = models.VoteTally(
            booth=booth_yossarian_3, election=house_election_2010,
            candidate=eighth, primary_votes=841, tcp_votes=0)
        tally_yossarian_3_eighth_2010.save()
        tally_yossarian_3_eighth_2013 = models.VoteTally(
            booth=booth_yossarian_3, election=house_election_2013,
            candidate=eighth, primary_votes=683, tcp_votes=0)
        tally_yossarian_3_eighth_2013.save()