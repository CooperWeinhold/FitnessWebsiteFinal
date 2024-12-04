# myapp/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

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
