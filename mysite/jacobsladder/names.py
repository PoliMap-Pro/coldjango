from django.db import models


class TrackedName(models.Model):
    class Meta:
        abstract = True
        app_label = 'jacobsladder'

    name = models.CharField(max_length=63)
    created = models.DateTimeField(auto_now_add=True)