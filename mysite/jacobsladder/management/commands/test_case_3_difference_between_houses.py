from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    help = "Get me the Greens senate first pref vote in each seat, as well " \
           "as the reps first pref vote, and calculate the delta. Do this " \
           "over time from 2001\n\n" \
           ""

    AEC_RESULTS = {}

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        print("\n")
        for election in models.SenateElection.objects.all().order_by(
                'election_date'):
            print(f"Election on {election.election_date}")
            all_lighthouses = election.lighthouses.all().order_by('name')
            house_election = models.HouseElection.objects.get(
                election_date=election.election_date)
            all_seats = house_election.seats.all().order_by('name')
            both_houses = zip(all_lighthouses, all_seats)
            [Command.find_difference(election, lighthouse, seat) for
             lighthouse, seat in both_houses]
            print()

    @staticmethod
    def find_difference(election, seat, lighthouse):
        result = Command.check_seat(election, seat) - \
                 Command.check_lighthouse(election, lighthouse)
        print('Difference', result)
        return result

    @staticmethod
    def check_seat(election, seat):
        representation = models.Representation.objects.get(
            election=election, party__abbreviation__iexact='GRN',
            person__candidate__contention__seat=seat,
            person__candidate__contention__election=election
        )
        result = seat.candidate_for(representation.person.candidate, election)
        print('House', result)
        return result

    @staticmethod
    def check_lighthouse(election, lighthouse):
        result = sum([vote_stack.primary_votes for floor in
                      models.Floor.objects.filter(lighthouse=lighthouse) for
                      selection in models.Selection.objects.filter(
                        election=election, party__abbreviation='GRN',
                        candidate__vote_stack__floor=floor,
                        candidate__vote_stack__lighthouse=lighthouse) for
                      vote_stack in models.VoteStack.objects.filter(
                        election=election, floor=floor, lighthouse=lighthouse,
                        candidate=selection.candidate)])
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



