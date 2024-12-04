# myapp/models.py
from django.db import models
from django.contrib.auth.models import User

# Fitness Profile linked to a user
class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female')
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Lightly active (light exercise/sports 1-3 days a week)'),
        ('moderate', 'Moderately active (moderate exercise/sports 3-5 days a week)'),
        ('active', 'Very active (hard exercise/sports 6-7 days a week)'),
        ('super_active', 'Super active (very hard exercise/physical job & exercise 2x/day)')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_weight = models.FloatField()
    goal_weight = models.FloatField()
    timeline = models.IntegerField(help_text="Timeline in weeks")
    height = models.FloatField(help_text="Height in cm", default=170)
    age = models.IntegerField(help_text="Age in years", default=25)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    activity_level = models.CharField(max_length=15, choices=ACTIVITY_LEVEL_CHOICES, default='sedentary')
    macros = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username

# Exercise Trackingi
class Exercise(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField()

