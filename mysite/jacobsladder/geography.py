from django.db import models
from . import section


class Pin(section.Part):
    class Meta:
        abstract = True

    location = models.OneToOneField('Geography', on_delete=models.SET_NULL,
                                    null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)