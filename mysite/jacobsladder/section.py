from django.db import models
import time

class Part(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def get_set(cls, selector):
        if selector:
            if isinstance(selector, dict):
                return cls.objects.filter(**selector)
            return selector
        return cls.objects.all()