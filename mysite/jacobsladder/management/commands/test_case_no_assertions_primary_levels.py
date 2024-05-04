from django.core.management.base import BaseCommand
from datetime import datetime
from ...models import HouseElection, Seat, Booth, VoteTally, Person, \
    HouseCandidate
from ...model_fields import StateName


class Command(BaseCommand):
    help = 'Primary ordinary votes at different levels'

    def handle(self, *arguments, **keywordarguments):
        twenty_twenty_two = datetime(year=2022, month=1, day=1)
        house_election_2022 = HouseElection.objects.get(election_date=twenty_twenty_two)
        seat = Seat.objects.get(name="Fenner", state=StateName.ACT)
        booth = Booth.objects.get(name="Gungahlin", seat=seat)
        person = Person.objects.get(name="LEIGH", other_names="Andrew")
        candidate = HouseCandidate.objects.get(person=person)

        def func(election):
            print(election)

        def func2(election, seat):
            print(election, seat)

        def func3(election, seat, booth):
            print(election, seat, booth)

        def func4(election, seat, booth, vote_tally):
            print(election, seat, booth, vote_tally)

        HouseElection.per(func)
        Seat.per(func2)(house_election_2022)
        HouseElection.per(Seat.per(func2))
        Booth.per(func3)(seat, house_election_2022)
        Seat.per(Booth.per(func3))(house_election_2022)
        HouseElection.per(Seat.per(Booth.per(func3)))
        VoteTally.per(func4)(booth, seat, house_election_2022)
        Booth.per(VoteTally.per(func4))(seat, house_election_2022)
        Seat.per(Booth.per(VoteTally.per(func4)))(house_election_2022)
        HouseElection.per(Seat.per(Booth.per(VoteTally.per(func4))))
        print(f"Primary vote for {person} in {house_election_2022}: "
              f"{seat.candidate_for(candidate, house_election_2022)}")