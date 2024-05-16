from datetime import datetime
from django.core.management.base import BaseCommand
from ... import house, service, place


class Command(BaseCommand):
    help = "Get all the seats in 2022 where a non-Greens/ALP/Lib polled more " \
           "than 10% primary\n" \
           "Adds up the results from the booths and asserts that the seats " \
           "where the total exceeds 10% are:\n"

    EXCLUDED_PARTIES = ('GRN', 'ALP', 'LP', 'LNP', 'NP' )
    TARGET = ('Bradfield', 'Calare', 'Capricornia', 'Clark', 'Cowper',
              'Curtin', 'Dawson', 'Fly', 'Fowler', 'Gippsland', 'Goldstein',
              'Grey', 'Hinkler', 'Hughes', 'Hume', 'Hunter', 'Indi', 'Kennedy',
              'Kooyong', 'Lingiari', 'Lyne', 'Lyons', 'Mackellar', 'Mallee',
              'Maranoa', 'Mayo', 'Monash', 'New England', 'Nicholls',
              'North Sydney', 'Page', 'Parkes', 'Richmond', 'Riverina',
              'Solomon', 'Spence', 'Wannon', 'Warringah', 'Wentworth',
              'Wright', )

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        print(Command.TARGET)
        print()
        twenty_twenty_two = house.HouseElection.objects.get(
            election_date=datetime(year=2022, month=1, day=1))
        result = []
        for seat in place.Seat.objects.all():
            total = seat.total_attribute(twenty_twenty_two, 'primary_votes')
            for contention in service.Contention.objects.filter(
                    election=twenty_twenty_two, seat=seat):
                party = service.Representation.objects.get(
                    person=contention.candidate.person,
                    election=twenty_twenty_two).party
                if party.abbreviation not in Command.EXCLUDED_PARTIES:
                    if party.name.lower() != 'informal':
                        primary = seat.candidate_for(contention.candidate,
                                                     twenty_twenty_two)
                        proportion = primary / total
                        if proportion > 0.1:
                            result.append(seat.name)
                            print(f"In {seat} {party.name} polled "
                                  f"{proportion * 100.0}%")
                            break
        for entry in result:
            assert entry in Command.TARGET
        for entry in Command.TARGET:
            assert entry in result

