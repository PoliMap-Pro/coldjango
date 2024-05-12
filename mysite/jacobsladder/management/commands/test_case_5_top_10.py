from operator import itemgetter
from django.core.management.base import BaseCommand
from ... import house


class Command(BaseCommand):
    help = "Get the top 10 greens seats by primary for each of the last 5 " \
           "elections.\n" \
           "Adds up the results from the booths and asserts that they " \
           "match:\n"

    TARGET = {('Batman', 2010, 14907),
              ('Batman', 2013, 18544),
              ('Batman', 2016, 26209),
              ('Batman', 2022, 14907),
              ('Brisbane', 2010, 13338),
              ('Brisbane', 2019, 17247),
              ('Brisbane', 2022, 13338),
              ('Brisbane', 2022, 20985),
              ('Canberra', 2010, 18142),
              ('Canberra', 2013, 12858),
              ('Canberra', 2016, 16659),
              ('Canberra', 2019, 17462),
              ('Canberra', 2022, 18142),
              ('Canberra', 2022, 19240),
              ('Cooper', 2022, 20025),
              ('Cunningham', 2022, 19125),
              ('Fenner', 2016, 16592),
              ('Fraser', 2010, 19435),
              ('Fraser', 2013, 15583),
              ('Fraser', 2022, 19435),
              ('Gellibrand', 2013, 11666),
              ('Gellibrand', 2016, 15855),
              ('Grayndler', 2010, 17723),
              ('Grayndler', 2013, 16882),
              ('Grayndler', 2016, 15962),
              ('Grayndler', 2019, 17721),
              ('Grayndler', 2022, 17723),
              ('Griffith', 2019, 19077),
              ('Griffith', 2022, 28146),
              ('Higgins', 2016, 17369),
              ('Higgins', 2019, 17653),
              ('Kooyong', 2019, 16387),
              ('Macnamara', 2019, 17665),
              ('Macnamara', 2022, 20478),
              ('Melbourne Ports', 2010, 13521),
              ('Melbourne Ports', 2013, 12342),
              ('Melbourne Ports', 2016, 15047),
              ('Melbourne Ports', 2022, 13521),
              ('Melbourne', 2010, 25702),
              ('Melbourne', 2013, 27645),
              ('Melbourne', 2016, 30808),
              ('Melbourne', 2019, 35227),
              ('Melbourne', 2022, 25702),
              ('Melbourne', 2022, 34398),
              ('Richmond', 2013, 12929),
              ('Richmond', 2016, 17575),
              ('Richmond', 2019, 17738),
              ('Richmond', 2022, 21265),
              ('Ryan', 2010, 13876),
              ('Ryan', 2022, 13876),
              ('Ryan', 2022, 22451),
              ('Sydney', 2010, 14607),
              ('Sydney', 2013, 11760),
              ('Sydney', 2022, 14607),
              ('Wills', 2010, 13436),
              ('Wills', 2013, 15244),
              ('Wills', 2016, 22325),
              ('Wills', 2019, 19994),
              ('Wills', 2022, 13436),
              ('Wills', 2022, 18503), }

    def handle(self, *arguments, **keywordarguments):
        last_year_in_target = max([year for _, year, _ in Command.TARGET])
        print(Command.help)
        print(Command.TARGET)
        print()
        print()
        last_five = house.HouseElection.objects.all().order_by(
            '-election_date__year')[:5]
        for election in last_five:
            print(election)
            print()
            totals = [(contention.seat.candidate_for(
                contention.candidate, election), contention.seat) for
                contention in election.get_contentions('GRN')]
            totals.sort(key=itemgetter(0))
            totals.reverse()
            top_ten = totals[:10]
            for total, seat in top_ten:
                if election.election_date.year <= last_year_in_target:
                    assert (seat.name, election.election_date.year, total) in \
                           Command.TARGET
                print(seat, total)
            print()






