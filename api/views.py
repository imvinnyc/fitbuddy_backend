# api/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_APP_KEY = os.getenv("NUTRITIONIX_APP_KEY")

EXERCISEDB_KEY = os.getenv("EXERCISEDB_API_KEY")
EXERCISEDB_HOST = os.getenv("EXERCISEDB_API_HOST", "exercisedb.p.rapidapi.com")


@csrf_exempt
def generate_workout(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    body_type = request.POST.get("body_type", "")
    goal = request.POST.get("goal", "")
    intensity = request.POST.get("intensity", "")
    duration = request.POST.get("duration", "")

    prompt = (
        f"Create a {duration}-minute {intensity} intensity workout plan "
        f"for someone whose goal is to {goal}. This person has a {body_type} body type."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a fitness coach."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )

    workout = response["choices"][0]["message"]["content"].strip()
    return JsonResponse({"workout": workout})


@csrf_exempt
def generate_diet(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    body_type = request.POST.get("body_type", "")
    goal = request.POST.get("goal", "")
    diet_preference = request.POST.get("diet_preference", "")

    prompt = (
        f"Create a balanced {diet_preference} diet plan for someone whose "
        f"goal is to {goal}. This person has a {body_type} body type."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a nutritionist."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )

    diet = response["choices"][0]["message"]["content"].strip()
    return JsonResponse({"diet": diet})


@csrf_exempt
def nutritionix(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    query = request.POST.get("query")
    food = request.POST.get("food")

    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_APP_KEY,
        "x-remote-user-id": "0",
    }

    if query:
        url = "https://trackapi.nutritionix.com/v2/search/instant"
        r = requests.get(url, headers=headers, params={"query": query})
        if r.status_code == 200:
            data = r.json()
            suggestions = [item["food_name"] for item in data.get("common", [])]
            return JsonResponse({"suggestions": suggestions})
        return JsonResponse({"error": "Nutritionix API error"}, status=r.status_code)

    if food:
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        r = requests.post(url, headers=headers, json={"query": food})
        if r.status_code == 200:
            foods = r.json().get("foods", [])
            result = {
                "Calories": sum(item.get("nf_calories", 0) for item in foods),
                "Fat": sum(item.get("nf_total_fat", 0) for item in foods),
                "Protein": sum(item.get("nf_protein", 0) for item in foods),
                "Carbohydrates": sum(item.get("nf_total_carbohydrate", 0) for item in foods),
                "Fiber": sum(item.get("nf_dietary_fiber", 0) for item in foods),
            }
            return JsonResponse(result)
        return JsonResponse({"error": "Nutritionix API error"}, status=r.status_code)

    return JsonResponse({"error": "Missing query or food parameter"}, status=400)


@csrf_exempt
def exercise_suggest(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    query = request.POST.get("query", "").strip()
    if not query:
        return JsonResponse({"suggestions": []})

    url = f"https://{EXERCISEDB_HOST}/exercises/name/{query}"
    headers = {
        "X-RapidAPI-Key": EXERCISEDB_KEY,
        "X-RapidAPI-Host": EXERCISEDB_HOST,
    }

    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            suggestions = [item.get("name", "") for item in data if "name" in item]
            return JsonResponse({"suggestions": suggestions})
    except Exception:
        pass

    return JsonResponse({"suggestions": []})


@csrf_exempt
def exercise_tutorial(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    exercise = request.POST.get("exercise", "").strip()
    if not exercise:
        return JsonResponse({"error": "Missing exercise parameter"}, status=400)

    tutorial_prompt = f"Provide a step-by-step tutorial on how to perform '{exercise}'."

    try:
        headers = {
            "X-RapidAPI-Key": EXERCISEDB_KEY,
            "X-RapidAPI-Host": EXERCISEDB_HOST,
        }
        url = f"https://{EXERCISEDB_HOST}/exercises/name/{exercise}"
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                item = data[0]
                equip = item.get("equipment", "none")
                body_part = item.get("bodyPart", "")
                target = item.get("target", "")
                tutorial_prompt = (
                    f"Provide a clear, step-by-step tutorial for the exercise '{exercise}'. "
                    f"Equipment needed: {equip}. Body part: {body_part}. Target muscle: {target}."
                )
    except Exception:
        pass

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a fitness coach."},
            {"role": "user", "content": tutorial_prompt},
        ],
        max_tokens=500,
        temperature=0.7,
    )

    tutorial = response["choices"][0]["message"]["content"].strip()
    return JsonResponse({"tutorial": tutorial})
