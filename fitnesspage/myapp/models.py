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

    @property
    def maintenance_calories(self):
        """
        Calculates maintenance calories using the Mifflin-St Jeor Equation.
        """
        if not (self.current_weight and self.height and self.age):
            return None

        # Convert weight to kg
        weight_kg = self.current_weight * 0.453592
        height_cm = self.height

        # Calculate Basal Metabolic Rate (BMR)
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * self.age)
        if self.gender == 'M':
            bmr += 5
        elif self.gender == 'F':
            bmr -= 161

        # Apply activity multiplier
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9,
        }
        multiplier = activity_multipliers.get(self.activity_level, 1.2)

        return round(bmr * multiplier, 2)

    def __str__(self):
        return f"{self.user.username}'s Profile"



    def __str__(self):
        return self.user.username

# Exercise Trackingi
class Exercise(models.Model):
        name = models.CharField(max_length=100, default='Unknown Exercise')
        description = models.TextField(default='No description')
        category = models.CharField(
            max_length=20,
            choices=[
                ('cardio', 'Cardio'),
                ('strength', 'Strength'),
                ('flexibility', 'Flexibility'),
                ('balance', 'Balance'),
            ],
            default='cardio',
        )
        difficulty = models.CharField(
            max_length=10,
            choices=[
                ('easy', 'Easy'),
                ('medium', 'Medium'),
                ('hard', 'Hard'),
            ],
            default='medium',
        )
        image = models.ImageField(upload_to='exercise_images/', null=True, blank=True)
        video_url = models.URLField(null=True, blank=True)  # Add video URL field

        #def __str__(self):
            #return self.name

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField()

