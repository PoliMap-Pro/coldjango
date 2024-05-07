from . import constants, base_code


class StringCode(str, base_code.BaseCode):
    def __new__(cls, parts, parts_dictionary,
                delimiter=constants.DEFAULT_DELIMITER):
        return str.__new__(cls, delimiter.join([parts_dictionary[part]
                                                if isinstance(
            part, super) else str(part) for part in parts]))

    @staticmethod
    def get_last_known(house_election, row):
        return StringCode((constants.CANDIDATE_CODE_HEADER,
                           constants.PARTY_ABBREVIATION_HEADER,
                           house_election.election_date.year), row)

