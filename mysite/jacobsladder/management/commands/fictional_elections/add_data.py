from datetime import datetime
from django.core.management.base import BaseCommand

import mysite.jacobsladder.house
import mysite.jacobsladder.people
import mysite.jacobsladder.place
import mysite.jacobsladder.service
from .... import model_fields
from .... import models


class Command(BaseCommand):
    help = 'Add data'

    def handle(self, *arguments, **keywordarguments):
        twenty_ten = datetime(year=2010, month=1, day=1)
        twenty_thirteen = datetime(year=2013, month=1, day=1)
        house_election_2010 = mysite.jacobsladder.house.HouseElection(election_date=twenty_ten)
        house_election_2010.save()
        house_election_2013 = mysite.jacobsladder.house.HouseElection(election_date=twenty_thirteen)
        house_election_2013.save()
        seat1 = mysite.jacobsladder.place.Seat(name="Frank", state=model_fields.StateName.VIC)
        seat1.save()
        seat1.elections.add(house_election_2010)
        seat1.elections.add(house_election_2013)
        seat2 = mysite.jacobsladder.place.Seat(name="Yossarian", state=model_fields.StateName.VIC)
        seat2.save()
        seat2.elections.add(house_election_2010)
        seat2.elections.add(house_election_2013)
        booth1 = mysite.jacobsladder.place.Booth()
        booth1.save()
        collection1 = mysite.jacobsladder.service.Collection(booth=booth1, seat=seat1,
                                                             election=house_election_2010)
        collection1.save()
        collection2 = mysite.jacobsladder.service.Collection(booth=booth1, seat=seat1,
                                                             election=house_election_2013)
        collection2.save()
        booth2 = mysite.jacobsladder.place.Booth()
        booth2.save()
        collection3 = mysite.jacobsladder.service.Collection(booth=booth2, seat=seat2,
                                                             election=house_election_2010)
        collection3.save()
        booth3 = mysite.jacobsladder.place.Booth()
        booth3.save()
        collection4 = mysite.jacobsladder.service.Collection(booth=booth3, seat=seat2,
                                                             election=house_election_2013)
        collection4.save()
        booth5 = mysite.jacobsladder.place.Booth()
        booth5.save()
        collection5 = mysite.jacobsladder.service.Collection(booth=booth5, seat=seat1,
                                                             election=house_election_2010)
        collection5.save()
        aap = mysite.jacobsladder.people.Party(name="Australian Apathy Party", abbreviation="AAP")
        aap.save()
        wta = mysite.jacobsladder.people.Party(name="World Tory Alliance", abbreviation="WTA")
        wta.save()
        guy = mysite.jacobsladder.people.Person(name="Party Hack")
        guy.save()
        other_guy = mysite.jacobsladder.people.Person(name="Dangerous Idealogue")
        other_guy.save()
        third_guy = mysite.jacobsladder.people.Person(name="Narcissist")
        third_guy.save()
        fourth_guy = mysite.jacobsladder.people.Person(name="Crypto-Fascist")
        fourth_guy.save()
        fifth_guy = mysite.jacobsladder.people.Person(name="Bored Billionaire")
        fifth_guy.save()
        sixth_guy = mysite.jacobsladder.people.Person(name="Scandal Magnet")
        sixth_guy.save()
        hack = mysite.jacobsladder.house.HouseCandidate(person=guy)
        hack.save()
        hack_for_aap_2010 = mysite.jacobsladder.service.Representation(person=guy, party=aap,
                                                                       election=house_election_2010)
        hack_for_aap_2010.save()
        contention1 = mysite.jacobsladder.service.Contention(candidate=hack, seat=seat1,
                                                             election=house_election_2010)
        contention1.save()
        imp = mysite.jacobsladder.house.HouseCandidate(person=other_guy)
        imp.save()
        imp_for_run_2010 = mysite.jacobsladder.service.Representation(person=other_guy, party=wta,
                                                                      election=house_election_2010)
        imp_for_run_2010.save()
        contention2 = mysite.jacobsladder.service.Contention(candidate=imp, seat=seat1,
                                                             election=house_election_2010)
        contention2.save()
        contention3 = mysite.jacobsladder.service.Contention(candidate=imp, seat=seat1,
                                                             election=house_election_2013)
        contention3.save()
        noise = mysite.jacobsladder.house.HouseCandidate(person=third_guy)
        noise.save()
        noise_for_run_2013 = mysite.jacobsladder.service.Representation(person=third_guy, party=wta,
                                                                        election=house_election_2013)
        noise_for_run_2013.save()
        contention4 = mysite.jacobsladder.service.Contention(candidate=noise, seat=seat1,
                                                             election=house_election_2010)
        contention4.save()
        contention5 = mysite.jacobsladder.service.Contention(candidate=noise, seat=seat2,
                                                             election=house_election_2013)
        contention5.save()
        fourth = mysite.jacobsladder.house.HouseCandidate(person=fourth_guy)
        fourth.save()
        fourth_for_run_2010 = mysite.jacobsladder.service.Representation(
            person=fourth_guy, party=wta, election=house_election_2010)
        fourth_for_run_2010.save()
        contention6 = mysite.jacobsladder.service.Contention(candidate=fourth, seat=seat2,
                                                             election=house_election_2010)
        contention6.save()
        fifth = mysite.jacobsladder.house.HouseCandidate(person=fifth_guy)
        fifth.save()
        contention7 = mysite.jacobsladder.service.Contention(candidate=fifth, seat=seat2,
                                                             election=house_election_2010)
        contention7.save()
        contention8 = mysite.jacobsladder.service.Contention(candidate=fifth, seat=seat2,
                                                             election=house_election_2013)
        contention8.save()
        sixth = mysite.jacobsladder.house.HouseCandidate(person=sixth_guy)
        sixth.save()
        sixth_for_aap_2013 = mysite.jacobsladder.service.Representation(person=sixth_guy, party=aap,
                                                                        election=house_election_2013)
        sixth_for_aap_2013.save()
        contention9 = mysite.jacobsladder.service.Contention(candidate=sixth, seat=seat1,
                                                             election=house_election_2013)
        contention9.save()
