from django.db import models
from . import section, constants


class Pin(section.Part):
    class Meta:
        abstract = True

    location = models.OneToOneField('Geography', on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def add_transaction_pieces(self, representation, result,
                               tally_attribute, total, votes):
        [result.append({constants.RETURN_NAME: name_part,
                        constants.RETURN_VALUES: values_part}) for
         name_part, values_part in self.__class__.transaction_format_pieces(
            representation, tally_attribute, votes, total)]

    def format_results(self, representation, result, return_format,
                       tally_attribute, total, votes):
        if return_format == constants.TRANSACTION_FORMAT:
            self.add_transaction_pieces(representation, result, tally_attribute,
                                        total, votes)
        else:
            self.__class__.update_result(result, representation, votes, total)

    @staticmethod
    def update_result(result, representation, votes, total):
        result[str(representation.party)] = {
            constants.RETURN_VOTES: votes, constants.RETURN_PERCENTAGE:
                100.0 * votes / total}

    @staticmethod
    def transaction_format_pieces(represen, tally_attribute, vote_like, total):
        return ((constants.RETURN_GROUPING, [str(represen.party)]), (
            tally_attribute, [vote_like]), (constants.RETURN_PERCENTAGE, [
            100 * vote_like / total]))