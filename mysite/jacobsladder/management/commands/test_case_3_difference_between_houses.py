from django.core.management.base import BaseCommand
from ... import models, house, place, service


class Command(BaseCommand):
    help = "Get me the Greens senate first pref vote in each seat, as well " \
           "as the reps first pref vote, and calculate the delta. Do this " \
           "over time from 2001\n\n" \
           "Fetches the number of primary votes for each seat in both houses.\n\n" \
           "Asserts that a sample of ten from each house match the numbers " \
           "from https://results.aec.gov.au, which are:\n\n" \
           "SENATE\n" \
           "('Bennelong', '2016'): 6210,\n" \
           "('Boothby', '2019'): 14185,\n" \
           "('Bruce', '2007'): 4004,\n" \
           "('Fraser', '2010'): 25156,\n" \
           "('Gellibrand', '2019'): 11638,\n" \
           "('Grayndler', '2013'): 18625,\n" \
           "('Hasluck', '2022'): 9829,\n" \
           "('Lingiari', '2004'): 2554,\n" \
           "('Newcastle', '2022'): 17868,\n" \
           "('Wide Bay', '2019'): 6771\n\n" \
           "HOUSE\n" \
           "('Bennelong', '2016'): 6660,\n" \
           "('Boothby', '2019'): 10695,\n" \
           "('Bruce', '2007'): 3231,\n" \
           "('Fraser', '2010'): 19435,\n" \
           "('Gellibrand', '2019'): 13077,\n" \
           "('Grayndler', '2013'): 16882,\n" \
           "('Hasluck', '2022'): 7928,\n" \
           "('Lingiari', '2004'): 1893,\n" \
           "('Newcastle', '2022'): 21195,\n" \
           "('Wide Bay', '2019'): 7486\n\n"

    SENATE_RESULTS = {('Bennelong', '2016'): 6210,
                     ('Boothby', '2019'): 14185,
                     ('Bruce', '2007'): 4004,
                     ('Fraser', '2010'): 25156,
                     ('Gellibrand', '2019'): 11638,
                     ('Grayndler', '2013'): 18625,
                     ('Hasluck', '2022'): 9829,
                     ('Lingiari', '2004'): 2554,
                     ('Newcastle', '2022'): 17868,
                     ('Wide Bay', '2019'): 6771, }
    HOUSE_RESULTS = {('Bennelong', '2016'): 6660,
                     ('Boothby', '2019'): 10695,
                     ('Bruce', '2007'): 3231,
                     ('Fraser', '2010'): 19435,
                     ('Gellibrand', '2019'): 13077,
                     ('Grayndler', '2013'): 16882,
                     ('Hasluck', '2022'): 7928,
                     ('Lingiari', '2004'): 1893,
                     ('Newcastle', '2022'): 21195,
                     ('Wide Bay', '2019'): 7486, }

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        for election in models.SenateElection.objects.all().order_by(
                'election_date'):
            print(f"Election on {election.election_date}")
            all_lighthouses = election.lighthouse_set.all().order_by('name')
            house_election = house.HouseElection.objects.get(
                election_date=election.election_date)
            all_seats = house_election.seat_set.all().order_by('name')
            both_houses = zip(all_lighthouses, all_seats)
            [Command.find_difference(election, house_election, seat,
                                     lighthouse) for lighthouse, seat in
             both_houses]
            print()

    @staticmethod
    def find_difference(election, house_election, seat, lighthouse):
        result = Command.check_seat(house_election, seat) - \
                 Command.check_lighthouse(election, lighthouse)
        print('Difference', result)
        return result

    @staticmethod
    def check_seat(election, seat):
        representation = service.Representation.objects.get(
            election=election, party__abbreviation__iexact='GRN',
            person__candidate__contention__seat=seat,
            person__candidate__contention__election=election
        )
        result = seat.candidate_for(representation.person.candidate, election)
        key = seat.name, election.election_year.year
        if key in Command.HOUSE_RESULTS:
            assert Command.HOUSE_RESULTS[key] == result
        print('House', result)
        return result

    @staticmethod
    def check_lighthouse(election, lighthouse):
        result = sum([votack.primary_votes for floor in
                      place.Floor.objects.filter(lighthouse=lighthouse) for
                      selection in service.Selection.objects.filter(
                        election=election, party__abbreviation__iexact='GRN')
                      for votack in models.VoteStack.objects.filter(
                        election=election, floor=floor, lighthouse=lighthouse,
                        candidate=selection.person.candidate)])
        key = lighthouse.name, election.election_year.year
        if key in Command.HOUSE_RESULTS:
            assert Command.SENATE_RESULTS[key] == result
        print('Senate', result)
        return result

        #for floor in models.Floor.objects.filter(lighthouse=lighthouse):
        #    for selection in models.Selection.objects.filter(
        #            election=election, party__abbreviation='GRN',
        #            candidate__vote_stack__floor=floor,
        #            candidate__vote_stack__lighthouse=lighthouse):
        #        for vote_stack in models.VoteStack.objects.filter(
        #                election=election, floor=floor, lighthouse=lighthouse,
        #                candidate=selection.candidate):
        #            vote_stack.primary_votes



