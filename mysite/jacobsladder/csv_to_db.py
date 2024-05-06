from operator import itemgetter
from . import models
from .aec_codes import StringCode
from .aec_readers import AECCodeReader
from .constants import ELECTION_DIRECTORIES


class ElectionReader(AECCodeReader):
    BOOTH_NAME_HEADER = 'PollingPlace'
    BOOTH_CODE_HEADER = 'PollingPlaceID'
    ENROLLMENT_HEADER = 'Enrolment'
    ROUND_NUMBER_HEADER = 'CountNumber'

    def map_report_with_blank_line(self, directory, election, quiet,
                                   single_create_method, text_to_print,
                                   line_before_headers=True):
        self.map_report(directory, election, quiet, single_create_method,
                        text_to_print, True, line_before_headers)

    def map_report_without_blank_line(self, directory, election, quiet,
                                      single_create_method, text_to_print,
                                      line_before_headers=True):
        self.map_report(directory, election, quiet, single_create_method,
                        text_to_print, False, line_before_headers)

    @staticmethod
    def get_election_items(sort_key=itemgetter(0)):
        election_items = list(ELECTION_DIRECTORIES.items())
        election_items.sort(key=sort_key)
        election_items.reverse()
        return election_items

    @staticmethod
    def fetch_party(row, bind=models.Party):
        party_name = row[StringCode.PARTY_NAME_HEADER]
        if party_name:
            party_abbreviation = row[StringCode.PARTY_ABBREVIATION_HEADER]
            if party_abbreviation:
                party, _ = bind.objects.get_or_create(
                    name=party_name, abbreviation=party_abbreviation)
                return party
        return None

    @staticmethod
    def fetch_pref_data(house_election, reader, round_objects, row):
        candidate, received, seat = ElectionReader.fetch_candid(house_election,
                                                                row)
        transferred = ElectionReader.advance(reader)
        round_obj, _ = round_objects.get_or_create(
            seat=seat, election=house_election,
            round_number=int(row[ElectionReader.ROUND_NUMBER_HEADER]))
        return candidate, round_obj, received, received, seat, transferred

    @staticmethod
    def find_seat(house_election, row, beacon_objects=models.Seat.objects):
        seat = ElectionReader.set_seat_election(beacon_objects, house_election,
                                                row)
        seat.state = row[StringCode.STATE_ABBREVIATION_HEADER].lower()
        seat.save()
        return seat

    @staticmethod
    def add_one_seat(election, row, code_objects=models.SeatCode.objects):
        seat = ElectionReader.find_seat(election, row)
        seat_code, _ = code_objects.get_or_create(
            seat=seat, number=int(row[ElectionReader.SEAT_CODE_HEADER]))
        enrollment, _ = models.Enrollment.objects.get_or_create(
            seat=seat, election=election, number_enrolled=int(
                row[ElectionReader.ENROLLMENT_HEADER]))
