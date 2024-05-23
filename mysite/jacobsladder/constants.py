ELECTION_DIRECTORIES = {year: f".\\jacobsladder\\{year}\\" for year in
                        (2022, 2019, 2016, 2013, 2010, 2007, 2004)}

ABSENT_HEADER = "AbsentVotes"
ATTRIBUTE_NAME = 'attribute'
BOOTHS_DIRECTORY_RELATIVE = "house_prefs\\"
CANDIDATE_CODE_HEADER = 'CandidateID'
CANDIDATE_DIRECTORY_RELATIVE = "senate_candidates\\"
DATA = 'data'
DECLARATION_HEADER = "PrePollVotes"
DEFAULT_DELIMITER = "-"
DEFAULT_FILE_EXTENSION_FOR_SOURCE_FILES = ".csv"
FLOORS_DIRECTORY_RELATIVE = "senate_prefs\\"
HOUSE_DISTRIBUTION_DIRECTORY_RELATIVE = "house_distribution_of_preferences\\"
INFORMAL_VOTER = 'informal'
LIGHTHOUSES_DIRECTORY_RELATIVE = "senate_votes_counted\\"
NAMES = 'names'
NEST_FORMAT = "nest_format"
PARTY_ABBREVIATION_HEADER = 'PartyAb'
PARTY_NAME_HEADER = 'PartyNm'
PLACE_NAME = 'place'
POSTAL_HEADER = "PostalVotes"
PROVISIONAL_HEADER = "ProvisionalVotes"
QUERIES = 'queries'
RETURN_GROUPING = 'party'
RETURN_NAME = 'name'
RETURN_PERCENTAGE = 'percent'
RETURN_VALUES = 'values'
RETURN_VOTES = 'votes'
RETURN_YEAR = 'year'
SEATS_DIRECTORY_RELATIVE = "house_votes_counted\\"
SENATE_DISTRIBUTION_DIRECTORY_RELATIVE = "senate_distribution_of_preferences\\"
SERIES = 'series'
SPREADSHEET_FORMAT = 'spreadsheet_format'
SPREADSHEET_FORMAT_ATTRIBUTE_INDEX = 2
SPREADSHEET_FORMAT_PARTY_INDEX = 3
SPREADSHEET_FORMAT_PERCENT_INDEX = 5
SPREADSHEET_FORMAT_PLACE_INDEX = 1
SPREADSHEET_FORMAT_VOTES_INDEX = 4
SPREADSHEET_FORMAT_YEAR_INDEX = 0
STATE_ABBREVIATION_HEADER = 'StateAb'
SWING_HEADER = "Swing"
TOTAL_HEADER = "TotalVotes"
TRANSACTION_FORMAT = "transaction_format"
TWO_CANDIDATE_DIRECTORY_RELATIVE = "two_candidate_preferred\\"
TYPES_DIRECTORY_RELATIVE = "seats\\"

SPREADSHEET_NAMES = (RETURN_YEAR, PLACE_NAME, ATTRIBUTE_NAME, RETURN_GROUPING,
                     RETURN_VOTES, RETURN_PERCENTAGE, )

ABBREVIATION_LIST = ['IND', 'UAPP', 'ON', 'LP', 'NAFD', 'AJP', 'IMO', 'CYA',
                     'CLP', 'CEC', 'LDP', 'AUVA', 'SOPA', 'DPDA', 'TNL',
                     'JLN', 'VNS', 'SAL', 'GAP', 'AUP', 'CDP', 'RUA',
                     'FACN', 'WAP', 'BTA', 'FFP', 'ASP', 'CEC', 'XEN',
                     'REP', 'ARF', 'SPA', 'KAP', 'FNPP', 'AIN', 'ASXP',
                     'DEM', 'NCO', 'TGA', 'NGST', ]
