# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

User = get_user_model()


ACCEPT_CHOICES = (
    ("Y", _("Accept")),
    ("N", _("Reject")),
)


class Consent(models.Model):
    """
    Record the explicit consent of a User to a purpose
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=64)
    creation_time = models.DateTimeField(auto_now_add=True)
    # accepted is null if user has not yet consented to a purpose, but should
    accepted = models.CharField(
        max_length=1,
        null=True,
        blank=False,
        choices=ACCEPT_CHOICES,
    )
