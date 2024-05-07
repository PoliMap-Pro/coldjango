from . import models, aec_readers, folder_reader


class AECCodeReader(aec_readers.AECReader):
    ALTERNATIVE_BALLOT_ORDER_HEADER = 'Ballot Position'
    BALLOT_ORDER_HEADER = 'BallotPosition'
    KIND_OF_VOTES_HEADER = 'CalculationType'
    NUMBER_OF_VOTES_HEADER = 'CalculationValue'
    ORDINARY_VOTES_HEADER = 'OrdinaryVotes'

    def map_report(self, directory, election, quiet, single_create_method,
                   text_to_print, blank_line, line_before_headers=True,
                   two_header_years=None, election_year=None):
        folder_reader.FolderReader.echo(quiet, text_to_print, blank_line)
        [self.add_one(filename, election, single_create_method,
                      line_before_headers, two_header_years,
                      election_year=election_year) for filename in
         folder_reader.FolderReader.walk(directory)]

    @staticmethod
    def print_year(election_year, print_before_year, quiet):
        if not quiet:
            print(print_before_year, election_year)
            print()

    @staticmethod
    def set_seat_election(beacon_objects, house_election, row):
        seat, _ = beacon_objects.get_or_create(name=row[
            aec_readers.AECReader.SEAT_NAME_HEADER])
        seat.elections.add(house_election)
        return seat

    @staticmethod
    def fetch_candid(house_election, row):
        """
        Fetch the person, then use it to fetch the candidate
        """

        candidate, seat = AECCodeReader.find_candidate_for_seat(house_election,
                                                                row)
        return candidate, int(row[AECCodeReader.NUMBER_OF_VOTES_HEADER]), seat

    @staticmethod
    def advance(reader):
        next(reader)
        return int(next(reader)[AECCodeReader.NUMBER_OF_VOTES_HEADER])

    @staticmethod
    def get_two_candidate_pref_votes(booth, candidate, house_election, row):
        vote_tally = models.VoteTally.objects.get(booth=booth,
                                                  election=house_election,
                                                  candidate=candidate)
        vote_tally.tcp_votes = int(row[AECCodeReader.ORDINARY_VOTES_HEADER])
        vote_tally.save()