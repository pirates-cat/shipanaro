# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Consent(models.Model):
    user = models.ForeignKey(User)
    purpose = models.CharField(max_length=64)
    creation_time = models.DateTimeField(auto_now_add=True)
