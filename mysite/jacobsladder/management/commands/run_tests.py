from django.core.management.base import BaseCommand
from . import test_case_1_primary_in_wills, test_case_2_by_booth_in_aston_2019, \
    test_case_4_no_assertions_house_flow, test_case_5_top_10, \
    test_case_6_minor_candidates, \
    test_case_9_no_assertions_primary_by_booth_in_aston_2022, call_endpoints

class Command(BaseCommand):
    help = "Calls test cases"

    def handle(self, *arguments, **keywordarguments):
        for command in (
                call_endpoints,
                test_case_1_primary_in_wills,
                test_case_2_by_booth_in_aston_2019,
                test_case_4_no_assertions_house_flow,
                test_case_5_top_10, test_case_6_minor_candidates,
                test_case_9_no_assertions_primary_by_booth_in_aston_2022):
            com = command.Command()
            com.handle(*arguments, **keywordarguments)

