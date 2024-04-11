from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    """ Should print,
    Election on 2010-01-01
        Seat of Frank
                Booth object (18)
                        Party Hack, Australian Apathy Party, 3424
                        Outmaneuvered Idealist, Independent, 424
                        Dangerous Idealogue, World Tory Alliance, 123
                        Narcissist, Independent, 45
                Booth object (21)
                        Party Hack, Australian Apathy Party, 6848
                        Outmaneuvered Idealist, Independent, 848
                        Dangerous Idealogue, World Tory Alliance, 246
                        Narcissist, Independent, 80

        Seat of Yossarian
                Booth object (19)
                        Crypto-Fascist, World Tory Alliance, 456
                        Bored Billionaire, Independent, 77
                        Rural Blowhard, Independent, 162
                Booth object (22)
                        Rural Blowhard, Independent, 841


Election on 2013-01-01
        Seat of Frank
                Booth object (18)
                        Outmaneuvered Idealist, Independent, 848
                        Scandal Magnet, Australian Apathy Party, 2345
                        Dangerous Idealogue, Independent, 3453

        Seat of Yossarian
                Booth object (20)
                        Narcissist, World Tory Alliance, 1564
                        Bored Billionaire, Independent, 64
                        Rural Blowhard, Independent, 261
                Booth object (22)
                        Narcissist, World Tory Alliance, 2018
                        Bored Billionaire, Independent, 18
                        Rural Blowhard, Independent, 683
    """

    help = 'Case 1'

    def handle(self, *arguments, **keywordarguments):
        for election in models.HouseElection.objects.all().order_by(
                'election_date'):
            print(f"Election on {election.election_date}")
            for seat in election.seat_set.all():
                print(f"\tSeat of {seat.name}")
                for collection in models.Collection.objects.filter(
                        seat=seat, election=election):
                    print(f"\t\t{collection.booth}")
                    models.VoteTally.per(Command.show_candidate)(
                        collection.booth, seat=seat, election=election)
                print()
            print()

    @staticmethod
    def show_candidate(election, seat, booth, vote_tally):
        if models.Representation.objects.filter(
                election=election,
                person=vote_tally.candidate.person).exists():
            middle = models.Representation.objects.get(
                election=election,
                person=vote_tally.candidate.person).party.name
        else:
            middle = "Independent"
        print(f"\t\t\t{vote_tally.candidate.person.name}, "
              f"{middle}, {vote_tally.primary_votes}")




