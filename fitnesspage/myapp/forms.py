# myapp/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Meal, WeightTracking

# User Registration Form (customize fields if needed)
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

# Profile Form for Fitness Goalsi
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['current_weight', 'goal_weight', 'timeline', 'height', 'age', 'gender', 'activity_level']

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['meal_name', 'calories', 'protein', 'carbs', 'fats']
        widgets = {
            'meal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control'}),
            'fats': forms.NumberInput(attrs={'class': 'form-control'}),
        }



class WeightForm(forms.ModelForm):
    class Meta:
        model = WeightTracking
        fields = ['date', 'weight']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }
