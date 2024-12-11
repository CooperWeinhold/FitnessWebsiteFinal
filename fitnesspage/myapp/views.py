# myapp/views.py
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import RegisterForm, ProfileForm, MealForm, WeightForm
from django.db.models import Sum
from .models import Profile, Exercise, Progress, Meal, WeightTracking
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.shortcuts import render
import json, requests
from django.conf import settings


# Recipe View Function
def recipes(request):
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
    }

    query_params = {
        "query": "healthy",
        "number": 9,
        "addRecipeInformation": "true",
        "addRecipeNutrition": "true",  # Include nutrition information
    }

    search_query = request.GET.get("search")
    if search_query:
        query_params["query"] = search_query

    try:
        # Debug: Log API request details
        print(f"API Request URL: {url}")
        print(f"Headers: {headers}")
        print(f"Query Params: {query_params}")

        # Make the API call
        response = requests.get(url, headers=headers, params=query_params)
        response.raise_for_status()

        # Debug: Log API response details
        data = response.json()
        print(f"API Response: {data}")

        # Extract relevant recipe data
        recipes = [
            {
                "id": recipe.get("id"),
                "title": recipe.get("title"),
                "image": recipe.get("image"),
                "summary": recipe.get("summary"),
                "calories": next(
                    (n["amount"] for n in recipe.get("nutrition", {}).get("nutrients", []) if n["name"] == "Calories"), None
                ),
                "carbs": next(
                    (n["amount"] for n in recipe.get("nutrition", {}).get("nutrients", []) if n["name"] == "Carbohydrates"), None
                ),
                "protein": next(
                    (n["amount"] for n in recipe.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), None
                ),
                "fat": next(
                    (n["amount"] for n in recipe.get("nutrition", {}).get("nutrients", []) if n["name"] == "Fat"), None
                ),
            }
            for recipe in data.get("results", [])
        ]

    except requests.exceptions.RequestException as e:
        # Debug: Log API error
        print(f"API Error: {e}")
        recipes = []

    return render(request, 'myapp/recipes.html', {"recipes": recipes, "search_query": search_query or ""})

def new_homepage(request):
    return render(request, 'myapp/new_homepage.html')




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
            return HttpResponseRedirect(reverse('new_homepage'))  # Redirect to profile after successful login
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
    default_exercises = [
        {
            "name": "Bench Press",
            "description": "A classic chest exercise, done by pressing the barbell up and down.",
            "category": "strength",
            "difficulty": "hard",
            "video_url": "https://www.youtube.com/embed/lWFknlOTbyM"
        },
        {
            "name": "Back Squat",
            "description": "One of the best overall leg exercises, make sure you keep your back straight and feet shoulder width apart.",
            "category": "strength",
            "difficulty": "hard",
            "video_url": "https://www.youtube.com/embed/aOzrA4FgnM0"
        },
        {
            "name": "Power Clean",
            "description": "A great full body exercise.",
            "category": "strength",
            "difficulty": "hard",
            "video_url": "https://www.youtube.com/embed/E2z5zK5V-MM"
        },
        {
            "name": "Push-Ups",
            "description": "Start in a high plank position, lower your chest to the floor, then push back up.",
            "category": "strength",
            "difficulty": "medium",
            "video_url": "https://www.youtube.com/embed/IODxDxX7oi4"
        },
        {
            "name": "Jumping Jacks",
            "description": "A cardio exercise to warm up your body.",
            "category": "cardio",
            "difficulty": "easy",
            "video_url": "https://www.youtube.com/embed/uLVt6u15L98"
        },
        {
            "name": "Burpees",
            "description": "Start in a standing position, drop into a squat, kick your legs back, then return to standing, repeat.",
            "category": "cardio",
            "difficulty": "hard",
            "video_url": "https://www.youtube.com/embed/qLBImHhCXSw"
        },
        {
            "name": "Lunges",
            "description": "Step forward with one leg and lower your hips until both knees are bent at 90-degree angles.",
            "category": "strength",
            "difficulty": "medium",
            "video_url": "https://www.youtube.com/embed/MxfTNXSFiYI"
        },
        {
            "name": "Stretching",
            "description": "A proper stretching routine is essential for muscle recovery/growth.",
            "category": "flexibility",
            "difficulty": "easy",
            "video_url": "https://www.youtube.com/embed/FI51zRzgIe4"
        },
        {
            "name": "Improving Balance",
            "description": "Having good balance is great for daily functionality as well as being safe incase of a fall",
            "category": "balance",
            "difficulty": "easy",
            "video_url": "https://www.youtube.com/embed/SzbVLVxXO0s"
        },{
            "name": "Dumbbell Curls",
            "description": "One of the most well known arm exercise to hit the biceps.",
            "category": "strength",
            "difficulty": "medium",
            "video_url": "https://www.youtube.com/embed/ykJmrZ5v0Oo"
        },{
            "name": "Cable Triceps Pushdown",
            "description": "Great movement utilizing a cable machine to hit the triceps.",
            "category": "strength",
            "difficulty": "medium",
            "video_url": "https://www.youtube.com/embed/-zLyUAo1gMw"
        },{
            "name": "Hammer Curls",
            "description": "A variation of the classic dumbbell curl.",
            "category": "strength",
            "difficulty": "medium",
            "video_url": "https://www.youtube.com/embed/BRVDS6HVR9Q"
        },
    ]

    for exercise_data in default_exercises:
        Exercise.objects.get_or_create(**exercise_data)

    # Get exercises, filtered by category and difficulty if specified
    category = request.GET.get('category', None)
    difficulty = request.GET.get('difficulty', None)
    exercises = Exercise.objects.all()

    if category:
        exercises = exercises.filter(category=category)
    if difficulty:
        exercises = exercises.filter(difficulty=difficulty)

    return render(request, 'myapp/exercises.html', {'exercises': exercises})
# Progress tracking page
def tracking(request):
    # Initialize forms
    meal_form = MealForm()
    weight_form = WeightForm()

    # Handle Meal Form Submission
    if request.method == "POST" and 'meal_submit' in request.POST:
        meal_form = MealForm(request.POST)
        if meal_form.is_valid():
            meal = meal_form.save(commit=False)
            meal.user = request.user
            meal.save()
            return redirect('tracking')  # Refresh to display updates

        # Handle clear action
        if request.method == "POST" and 'clear_meals' in request.POST:
            Meal.objects.filter(user=request.user).delete()
            return redirect('tracking')  # Refresh to display updates

    # Handle Weight Form Submission
    if request.method == "POST" and 'weight_submit' in request.POST:
        weight_form = WeightForm(request.POST)
        if weight_form.is_valid():
            weight_entry = weight_form.save(commit=False)
            weight_entry.user = request.user
            weight_entry.save()

    # Get Meal Data
    meals = Meal.objects.filter(user=request.user).order_by('-id')
    latest_meal = meals.first()


    # Get Weight Data
    weights = [
        {
            "date": item["date"].strftime('%Y-%m-%d'),
            "weight": item["weight"]
        }
        for item in WeightTracking.objects.filter(user=request.user).order_by('date').values('date', 'weight')
    ]

    # Pass data to the template
    return render(request, 'myapp/tracking.html', {
        'meal_form': meal_form,
        'meals': meals,
        'latest_meal': latest_meal,
        'weight_form': weight_form,
          # Convert to JSON string
        'weights': json.dumps(weights),  # Convert to JSON string
    })

# Recipe ideas page
