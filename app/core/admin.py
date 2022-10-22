import imp
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core import models

# Register your models here.

class UserAdmin(BaseUserAdmin):
    """Define the admin page users. """
    ordering = ['id']
    list_display=['email','name']

admin.site.register(models.User,UserAdmin)