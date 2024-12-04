# myapp/admin.py
from django.contrib import admin
from .models import Profile, Exercise, Progress

admin.site.register(Profile)
admin.site.register(Exercise)
admin.site.register(Progress)
