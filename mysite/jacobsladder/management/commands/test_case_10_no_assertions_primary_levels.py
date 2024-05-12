from django.core.management.base import BaseCommand
from datetime import datetime
from ... import people, house, place, model_fields


class Command(BaseCommand):
    help = 'Primary ordinary votes at different levels'

    def handle(self, *arguments, **keywordarguments):
        twenty_twenty_two = datetime(year=2022, month=1, day=1)
        house_election_2022 = house.HouseElection.objects.get(
            election_date=twenty_twenty_two)
        seat = house.Seat.objects.get(name="Fenner",
                                      state=model_fields.StateName.ACT)
        booth = place.Booth.objects.get(name="Gungahlin", seat=seat)
        person = people.Person.objects.get(name="LEIGH", other_names="Andrew")
        candidate = house.HouseCandidate.objects.get(person=person)

        def func(election):
            print(election)

        def func2(election, seat):
            print(election, seat)

        def func3(election, seat, booth):
            print(election, seat, booth)

        def func4(election, seat, booth, vote_tally):
            print(election, seat, booth, vote_tally)

        house.HouseElection.per(func)
        place.Seat.per(func2)(house_election_2022)
        house.HouseElection.per(place.Seat.per(func2))
        place.Booth.per(func3)(seat, house_election_2022)
        place.Seat.per(place.Booth.per(func3))(house_election_2022)
        house.HouseElection.per(place.Seat.per(place.Booth.per(func3)))
        house.VoteTally.per(func4)(booth, seat, house_election_2022)
        place.Booth.per(house.VoteTally.per(func4))(seat, house_election_2022)
        place.Seat.per(place.Booth.per(house.VoteTally.per(func4)))(
            house_election_2022)
        house.HouseElection.per(place.Seat.per(place.Booth.per(
            house.VoteTally.per(func4))))
        print(f"Primary vote for {person} in {house_election_2022}: "
              f"{seat.candidate_for(candidate, house_election_2022)}")