from django.urls import path
from api.views import (
    generate_workout,
    generate_diet,
    nutritionix,
    exercise_suggest,
    exercise_tutorial,
)

urlpatterns = [
    path('generate_workout/',   generate_workout),
    path('generate_diet/',      generate_diet),
    path('nutritionix/',        nutritionix),
    path('exercise_suggest/',   exercise_suggest),
    path('exercise_tutorial/',  exercise_tutorial),
]
