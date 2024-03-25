from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = 'Case 2'

    def handle(self, *arguments, **keywordarguments):
        pass




