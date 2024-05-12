from datetime import datetime
from django.core.management.base import BaseCommand

import mysite.jacobsladder.house
import mysite.jacobsladder.people
import mysite.jacobsladder.place
import mysite.jacobsladder.service
from .... import models


class Command(BaseCommand):
    help = 'Add votes'

    def handle(self, *arguments, **keywordarguments):
        seat2 = mysite.jacobsladder.place.Seat.objects.get(name="Yossarian")
        twenty_ten = datetime(year=2010, month=1, day=1)
        twenty_thirteen = datetime(year=2013, month=1, day=1)
        house_election_2010 = mysite.jacobsladder.house.HouseElection.objects.get(
            election_date=twenty_ten)
        house_election_2013 = mysite.jacobsladder.house.HouseElection.objects.get(
            election_date=twenty_thirteen)
        eighth_guy = mysite.jacobsladder.people.Person(name="Rural Blowhard")
        eighth_guy.save()
        eighth = mysite.jacobsladder.house.HouseCandidate(person=eighth_guy)
        eighth.save()
        contention_a = mysite.jacobsladder.service.Contention(candidate=eighth, seat=seat2,
                                                              election=house_election_2010)
        contention_a.save()
        contention_c = mysite.jacobsladder.service.Contention(candidate=eighth, seat=seat2,
                                                              election=house_election_2013)
        contention_c.save()
        booth_yossarian_1 = mysite.jacobsladder.place.Booth.objects.get(id=19)
        booth_yossarian_2 = mysite.jacobsladder.place.Booth.objects.get(id=20)
        booth_yossarian_3 = mysite.jacobsladder.place.Booth.objects.get(id=22)
        tally_yossarian_1_eighth_2010 = mysite.jacobsladder.house.VoteTally(
            booth=booth_yossarian_1, election=house_election_2010,
            candidate=eighth, primary_votes=162, tcp_votes=0)
        tally_yossarian_1_eighth_2010.save()
        tally_yossarian_1_eighth_2013 = mysite.jacobsladder.house.VoteTally(
            booth=booth_yossarian_1, election=house_election_2013,
            candidate=eighth, primary_votes=427, tcp_votes=0)
        tally_yossarian_1_eighth_2013.save()
        tally_yossarian_2_eighth_2010 = mysite.jacobsladder.house.VoteTally(
            booth=booth_yossarian_2, election=house_election_2010,
            candidate=eighth, primary_votes=686, tcp_votes=0)
        tally_yossarian_2_eighth_2010.save()
        tally_yossarian_2_eighth_2013 = mysite.jacobsladder.house.VoteTally(
            booth=booth_yossarian_2, election=house_election_2013,
            candidate=eighth, primary_votes=261, tcp_votes=0)
        tally_yossarian_2_eighth_2013.save()
        tally_yossarian_3_eighth_2010 = mysite.jacobsladder.house.VoteTally(
            booth=booth_yossarian_3, election=house_election_2010,
            candidate=eighth, primary_votes=841, tcp_votes=0)
        tally_yossarian_3_eighth_2010.save()
        tally_yossarian_3_eighth_2013 = mysite.jacobsladder.house.VoteTally(
            booth=booth_yossarian_3, election=house_election_2013,
            candidate=eighth, primary_votes=683, tcp_votes=0)
        tally_yossarian_3_eighth_2013.save()