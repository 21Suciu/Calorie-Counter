from django.shortcuts import render, redirect
import requests
from .models import FoodLog
from django.conf import settings
from datetime import date
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required


def search_food(request):
    food_data = []
    error_message = None

    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
            api_url = f'https://api.nal.usda.gov/fdc/v1/foods/search?query={query}&pageSize=25&api_key={settings.API_KEY}'

            try:
                # Make the API request
                response = requests.get(api_url)
                response.raise_for_status()  # Raise error for HTTP status codes >= 400

                # Get JSON response
                data = response.json()

                # Extract foods from the response
                food_data = [
                    {
                        'description': food.get('description'),
                        'foodNutrients': {
                            'ENERGY': next(
                                (nutrient['value'] for nutrient in food.get('foodNutrients', [])
                                 if nutrient['nutrientName'] == 'Energy'), 0
                            )
                        }
                    }
                    for food in data.get('foods', [])
                ]
                if not food_data:
                    error_message = "No matching foods found."

            except requests.exceptions.RequestException as e:
                error_message = f"API Request failed: {e}"
        else:
            error_message = "Please enter a valid search term."

    return render(request, 'calorie_app/search_food.html', {
        'food_data': food_data,
        'error_message': error_message,
    })


@login_required
def add_to_log(request):
    if request.method == 'POST':
        food_name = request.POST.get('food_name')
        calories_per_100g = request.POST.get('calories_per_100g')
        grams = request.POST.get('grams')

        if not food_name or not calories_per_100g or not grams:
            return render(request, 'calorie_app/search_food.html', {
                'error_message': 'All fields (food name, calories, and grams) are required to add to the log.'
            })

        try:
            grams = float(grams)
            calories_per_100g = float(calories_per_100g)

            # Calculate the actual calories eaten
            calories = (calories_per_100g / 100) * grams

            FoodLog.objects.create(
                user=request.user,
                food_name=food_name,
                calories=calories,
                portion_size=f"{grams}g"
            )
            return redirect('daily_log')
        except ValueError:
            return render(request, 'calorie_app/search_food.html', {
                'error_message': 'Invalid input for calories or grams.'
            })

    return redirect('search_food')


@login_required
def daily_log(request):
    # Get all food logs for today (filtered by date portion of the timestamp)
    food_logs = FoodLog.objects.filter(user=request.user, date=date.today())

    # Calculate total calories
    total_calories = sum(log.calories for log in food_logs)

    return render(request, 'calorie_app/daily_log.html', {
        'food_logs': food_logs,
        'total_calories': total_calories,
    })


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('daily_log')
    else:
        form = UserCreationForm()
    return render(request, 'calorie_app/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'calorie_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
