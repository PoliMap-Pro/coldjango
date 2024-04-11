from django.core.management.base import BaseCommand
from datetime import datetime

from ...models import HouseElection, Seat, Booth, VoteTally, Person, \
    HouseCandidate


class Command(BaseCommand):
    help = 'Unit test'

    def handle(self, *arguments, **keywordarguments):
        twenty_ten = datetime(year=2010, month=1, day=1)
        house_election_2010 = HouseElection.objects.get(
            election_date=twenty_ten)
        seat1 = Seat.objects.get(name="Frank")
        seat2 = Seat.objects.get(name="Yossarian")
        booth1 = Booth.objects.get(pk=21)
        hack_person = Person.objects.get(name="Party Hack")
        hack_candidate = HouseCandidate.objects.get(person=hack_person)

        def func(election):
            print(election)

        def func2(election, seat):
            print(election, seat)

        def func3(election, seat, booth):
            print(election, seat, booth)

        def func4(election, seat, booth, vote_tally):
            print(election, seat, booth, vote_tally)

        HouseElection.per(func)
        Seat.per(func2)(house_election_2010)
        HouseElection.per(Seat.per(func2))
        Booth.per(func3)(seat2, house_election_2010)
        Seat.per(Booth.per(func3))(house_election_2010)
        HouseElection.per(Seat.per(Booth.per(func3)))
        VoteTally.per(func4)(booth1, seat2, house_election_2010)
        Booth.per(VoteTally.per(func4))(seat2, house_election_2010)
        Seat.per(Booth.per(VoteTally.per(func4)))(house_election_2010)
        HouseElection.per(Seat.per(Booth.per(VoteTally.per(func4))))
        print(f"Primary vote for {hack_person} in {house_election_2010}: "
              f"{seat1.candidate_for(hack_candidate, house_election_2010)}")