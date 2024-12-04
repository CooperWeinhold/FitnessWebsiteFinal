# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import RegisterForm, ProfileForm
from .models import Profile, Exercise, Progress
from django.utils import timezone
from .models import Progress



# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in if authentication succeeds
            login(request, user)
            return HttpResponseRedirect(reverse('profile'))  # Redirect to profile after successful login
        else:
            # If authentication fails, send an error message to the template
            return render(request, 'myapp/login.html', {'error': 'Invalid username or password'})

    # Render the login page if it's a GET request
    return render(request, 'myapp/login.html')


# Register view
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, current_weight=0, goal_weight=0,
                                   timeline=0)  # Create profile with default values
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'myapp/register.html', {'form': form})


# myapp/views.py
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            profile.refresh_from_db()
            profile.macros = calculate_macros(
                current_weight=profile.current_weight,
                goal_weight=profile.goal_weight,
                height=profile.height,
                age=profile.age,
                gender=profile.gender,
                activity_level=profile.activity_level,
                timeline=profile.timeline
            )
            profile.save()
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'myapp/profile.html', {'form': form, 'profile': profile})



# Macro calculation helper function
# myapp/views.py
def calculate_macros(current_weight, goal_weight, height, age, gender, activity_level, timeline):
    # Convert weight from pounds to kg for the BMR calculation
    current_weight_kg = current_weight * 0.453592
    goal_weight_kg = goal_weight * 0.453592

    # Step 1: Calculate BMR using Mifflin-St Jeor Equation
    if gender == 'male':
        bmr = 10 * current_weight_kg + 6.25 * height - 5 * age + 5
    elif gender == 'female':
        bmr = 10 * current_weight_kg + 6.25 * height - 5 * age - 161

    # Step 2: Calculate TDEE based on activity level
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'super_active': 1.9
    }
    tdee = bmr * activity_factors.get(activity_level, 1.2)  # Default to sedentary if not set

    # Step 3: Determine the total caloric deficit or surplus needed
    weight_difference_kg = goal_weight_kg - current_weight_kg
    total_caloric_adjustment = weight_difference_kg * 7700  # 7700 calories per kg

    # Step 4: Calculate daily caloric adjustmenti
    days_to_goal = timeline * 7
    daily_caloric_adjustment = total_caloric_adjustment / days_to_goal

    # Step 5: Calculate the daily caloric intake goal
    if weight_difference_kg > 0:
        # Surplus for weight gain
        daily_caloric_intake = tdee + daily_caloric_adjustment
    else:
        # Deficit for weight loss
        daily_caloric_intake = tdee - abs(daily_caloric_adjustment)

    # Return the calculated daily caloric intake in a readable format
    return f"Calories: {daily_caloric_intake:.2f}"



# Exercises page
def exercises(request):
    exercises = [
        {'name': 'Push-up', 'description': 'An exercise to strengthen the chest, shoulders, and triceps.'},
        {'name': 'Squat', 'description': 'An exercise for the lower body, especially quads and glutes.'},
        {'name': 'Bench Press', 'description': 'An exercise that mainly focuses on the chest and some triceps.'},
        {'name': 'Dumbbell Curls', 'description': 'A classic exercise that strengthens the biceps'},
        {'name': 'Skull-Crushers', 'description': 'An over the head exercise that hits the triceps.'},
    ]
    return render(request, 'myapp/exercises.html', {'exercises': exercises})


# Progress tracking page
@login_required
def tracking(request):
    # Get the current year
    current_year = timezone.now().year

    # Retrieve the user's weight entries for the current year
    progress_data = Progress.objects.filter(user=request.user, date__year=current_year).order_by('date')

    # Prepare data for the chart
    labels = []
    weights = []
    for entry in progress_data:
        labels.append(entry.date.strftime('%b %d'))  # Format date as "Month Day", e.g., "Nov 10"
        weights.append(entry.weight)

    # Pass the labels and weights to the template for chart rendering
    return render(request, 'myapp/tracking.html', {
        'labels': labels,
        'weights': weights
    })


# Recipe ideas page
def recipes(request):
    recipes = [
        {'name': 'Avocado Toast', 'description': 'A quick breakfast with healthy fats and fiber.'},
        {'name': 'Chicken Salad', 'description': 'High-protein meal with vegetables and lean protein.'},
        {'name': 'Beef, potato, and egg bowl', 'description': 'A hearty solid meal filled with protein, carbs, and healthy fats.'},
    ]
    return render(request, 'myapp/recipes.html', {'recipes': recipes})
