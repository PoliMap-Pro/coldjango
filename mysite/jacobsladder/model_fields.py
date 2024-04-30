from django.db import models


class StateName(models.TextChoices):
    ACT = "act", "Australian Capital Territory"
    NSW = "nsw", "New South Wales"
    NT = "nt", "Northern Territory"
    QLD = "qld", "Queensland"
    SA = "sa", "South Australia"
    TAS = "tas", "Tasmania"
    VIC = "vic", "Victoria"
    WA = "wa", "Western Australia"