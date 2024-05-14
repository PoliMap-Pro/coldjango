from django.db import models
from . import section


class Pin(section.Part):
    class Meta:
        abstract = True

    location = models.OneToOneField('Geography', on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def update_result(result, representation, votes, total):
        #print(str(representation.party),  {
        #    'votes': votes, 'percent': 100.0 * votes / total})
        result[str(representation.party)] = {
            'votes': votes, 'percent': 100.0 * votes / total}