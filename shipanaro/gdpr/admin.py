from django.contrib import admin
from django.contrib.admin import ModelAdmin
from . import models


@admin.register(models.Consent)
class ConsentAdmin(ModelAdmin):
    list_display = ("user", "purpose", "accepted")
    search_fields = ("user", "purpose")
