import os
from datetime import datetime
from . import csv_to_db, place, service, constants, folder_reader, people, house


class BaseCode(csv_to_db.ElectionReader):
    def setup(self, booths_directory, house_election, seats_directory,
              two_candidate_preferred_directory, types_directory):
        self.add_seats(house_election, seats_directory)
        self.add_types(house_election, types_directory)
        self.add_booths(booths_directory, house_election)
        self.add_votes(house_election, two_candidate_preferred_directory)

    def add_booths(self, directory, election,
                   single_create_method='add_one_booth',
                   text_to_print="Reading files in booths directory",
                   quiet=False):
        self.map_report_with_blank_line(directory, election, quiet,
                                        single_create_method, text_to_print)

    def add_types(self, directory, election,
                  single_create_method='add_one_type',
                  text_to_print="Reading files in types directory",
                  quiet=False):
        self.map_report_with_blank_line(directory, election, quiet,
                                        single_create_method, text_to_print)

    def add_votes(self, election, directory,
                  single_create_method='add_one_tally',
                  text_to_print="Reading files in two candidate preferred "
                                "directory", quiet=False):
        folder_reader.FolderReader.echo(quiet, text_to_print)
        for filename in folder_reader.FolderReader.walk(directory):
            self.add_one(filename, election, single_create_method)
            folder_reader.FolderReader.echo(quiet, "", False)

    def add_seats(self, election, directory,
                  single_create_method='add_one_seat',
                  text_to_print="Reading files in seats directory",
                  quiet=False):
        self.map_report_without_blank_line(directory, election, quiet,
                                           single_create_method, text_to_print)

    @staticmethod
    def fetch_candidate(house_election, row, seat, tag=people.Party):
        candidate = BaseCode.pull_candidate(
            house_election, BaseCode.get_standard_person_attributes(row), row,
            seat)
        party, _ = tag.objects.get_or_create(name=row[
            constants.PARTY_NAME_HEADER], abbreviation=row[
            constants.PARTY_ABBREVIATION_HEADER])
        return candidate, party, candidate.person

    @staticmethod
    def set_booth_from_row(row, code_objects=place.SeatCode.objects):
        seat = BaseCode.fetch_by_aec_code(
            BaseCode.get_standard_beacon_attributes(row), place.Seat.objects,
            code_objects, 'seat', int(row[BaseCode.SEAT_CODE_HEADER]))
        booth, _ = place.Booth.objects.get_or_create(
            name=row[BaseCode.BOOTH_NAME_HEADER], seat=seat)
        booth_code, _ = place.BoothCode.objects.get_or_create(
            booth=booth, number=int(row[BaseCode.BOOTH_CODE_HEADER]))
        return booth, seat

    @staticmethod
    def add_one_type(house_election, row, code_objects=place.SeatCode.objects):
        seat = BaseCode.fetch_by_aec_code(
            BaseCode.get_standard_beacon_attributes(row), place.Seat.objects,
            code_objects, 'seat', int(row[BaseCode.SEAT_CODE_HEADER]))
        candidate, party, person = BaseCode.fetch_candidate(
            house_election, row, seat)
        vote_tally, _ = house.VoteTally.objects.get_or_create(
            bypass=seat, election=house_election, candidate=candidate,
            absent_votes=int(row[constants.ABSENT_HEADER]),
            provisional_votes=int(row[constants.PROVISIONAL_HEADER]),
            declaration_pre_poll_votes=int(row[constants.DECLARATION_HEADER]),
            postal_votes=int(row[constants.POSTAL_HEADER]),
            aec_ordinary=int(row[BaseCode.ORDINARY_VOTES_HEADER]),
            aec_total=int(row[constants.TOTAL_HEADER]),
            aec_swing=int(row[constants.SWING_HEADER]),)

    @staticmethod
    def set_ballot_position(candidate, house_election, party, person, row,
                            seat):
        representation, _ = service.Representation.objects.get_or_create(
            person=person, party=party, election=house_election)
        contention, _ = service.Contention.objects.get_or_create(
            seat=seat, candidate=candidate, election=house_election)
        contention.ballot_position = row[BaseCode.BALLOT_ORDER_HEADER]
        contention.save()

    @staticmethod
    def remove_extras(model_objects, attribute_dict):
        if model_objects.filter(**attribute_dict).count() > 1:
            modls = model_objects.filter(**attribute_dict)
            [extra.delete() for extra in modls[1:]]
            return modls[0]
        return False

    @staticmethod
    def start_election(election_year, folder, type_of_date=datetime,
                       print_before_year="Election", quiet=False):
        BaseCode.print_year(election_year, print_before_year, quiet)
        house_election, _ = house.HouseElection.objects.get_or_create(
            election_date=type_of_date(year=election_year, month=1, day=1))
        return os.path.join(folder, constants.BOOTHS_DIRECTORY_RELATIVE), \
            house_election, os.path.join(
            folder, constants.HOUSE_DISTRIBUTION_DIRECTORY_RELATIVE), \
            os.path.join(folder, constants.SEATS_DIRECTORY_RELATIVE), \
            os.path.join(folder, constants.TWO_CANDIDATE_DIRECTORY_RELATIVE), \
            os.path.join(folder, constants.TYPES_DIRECTORY_RELATIVE)