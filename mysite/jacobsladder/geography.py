from django.db import models
from . import section, constants


class Pin(section.Part):
    class Meta:
        abstract = True

    location = models.OneToOneField('Geography', on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def update_result(result, representation, votes, total):
        result[str(representation.party)] = {
            constants.RETURN_VOTES: votes, constants.RETURN_PERCENTAGE:
                100.0 * votes / total}