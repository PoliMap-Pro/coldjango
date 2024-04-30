import os


class StringCode(str):
    # Column headers from the csv files
    CANDIDATE_CODE_HEADER = 'CandidateID'
    PARTY_ABBREVIATION_HEADER = 'PartyAb'
    PARTY_NAME_HEADER = 'PartyNm'
    STATE_ABBREVIATION_HEADER = 'StateAb'

    DEFAULT_DELIMITER = "-"
    DEFAULT_FILE_EXTENSION_FOR_SOURCE_FILES = ".csv"

    def __new__(cls, parts, parts_dictionary, delimiter=DEFAULT_DELIMITER):
        return str.__new__(cls, delimiter.join([parts_dictionary[part]
                                                if isinstance(
            part, super) else str(part) for part in parts]))

    @staticmethod
    def walk(directory, file_extension=DEFAULT_FILE_EXTENSION_FOR_SOURCE_FILES):
        for base_path, directories, files in os.walk(directory):
            for file in files:
                if file.endswith(file_extension):
                    yield os.path.join(base_path, file)

    @staticmethod
    def get_last_known(house_election, row):
        return StringCode((StringCode.CANDIDATE_CODE_HEADER,
                           StringCode.PARTY_ABBREVIATION_HEADER,
                           house_election.election_date.year), row)

    @staticmethod
    def echo(quiet, text_to_print, blank_before=True):
        if not quiet:
            if blank_before:
                print()
            print(text_to_print)