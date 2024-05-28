from django.db import models
from . import geography, model_fields, names, section, constants


class Election(section.Part):
    DEFAULT_AFTER_END_OF_NAME = '/CED'
    DEFAULT_BETWEEN_PARTS_OF_NAME = "/"
    DEFAULT_PARTY_NAME_SEPARATOR = '_'

    class Meta:
        abstract = True
        app_label = "jacobsladder"

    election_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    def get_call_name(self, add_to_end_of_name, between_parts_of_name,
                      between_party_names, house_elections_text, p_set,
                      tally_attribute):
        """
        Smudges together the short names of the parties, the tally attribute and
        this election's year. Returns the result between house_elections_text at
        the front and add_to_end_of_name at the back
        """
        parties_string = between_party_names.join(set([p.short_name() for p in
                                                       p_set]))
        return f"{house_elections_text}{self.election_date.year}" \
               f"{between_parts_of_name}{tally_attribute}" \
               f"{between_parts_of_name}{parties_string}{add_to_end_of_name}"

    def format_result(self, elect_result, result, return_format):
        if return_format == constants.TRANSACTION_FORMAT:
            result[self.election_date.year] = elect_result
        elif return_format == constants.SPREADSHEET_FORMAT:
            pass
        else:
            result[str(self)] = elect_result

    def __str__(self):
        return f"{self.__class__.__name__} in " \
               f"{self.election_date.year} ({self.pk})"

    @staticmethod
    def by_votes(pair):
        return -pair[1]['votes']

    @staticmethod
    def format_return_for_transaction_format(elect_result, returned):
        total, query = returned
        if elect_result:
            elect_result[constants.QUERIES].append(str(query))
        return [], total

    @staticmethod
    def update_election_result_in_transaction_format(election_result, result,
                                                     tally_attribute):
        election_result[constants.DATA].append({
            constants.RETURN_NAME: tally_attribute,
            constants.RETURN_VALUES: result})


class Beacon(geography.Pin):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    state = models.CharField(max_length=9,
                             choices=model_fields.StateName.choices)


class Crown(models.Model):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    seat = models.ForeignKey('Seat', on_delete=models.CASCADE)
    election = models.ForeignKey('HouseElection', on_delete=models.CASCADE)


class Transfer(models.Model):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    votes_transferred = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)


class BallotEntry(Crown):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    ballot_position = models.PositiveSmallIntegerField(default=0)


class Club(names.TrackedName):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    def __str__(self):
        return self.name


class Transition(models.Model):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    reason = models.CharField(max_length=127)
    date_of_change = models.DateField()
    created = models.DateTimeField(auto_now_add=True)


class VoteRecord(models.Model):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    primary_votes = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)


class Contest(models.Model):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    state = models.CharField(max_length=9,
                             choices=model_fields.StateName.choices)
    election = models.ForeignKey("SenateElection", on_delete=models.CASCADE)


class Round(models.Model):
    class Meta:
        abstract = True
        app_label = "jacobsladder"

    round_number = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
