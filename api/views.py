from django.http import JsonResponse
import openai
import os
import requests
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


@csrf_exempt
def generate_workout(request):
    if request.method == 'POST':
        body_type = request.POST.get('body_type')
        goal = request.POST.get('goal')
        intensity = request.POST.get('intensity')
        duration = request.POST.get('duration')

        prompt = (
            f"Create a {duration}-minute {intensity} intensity workout plan for someone whose goal is to {goal}. "
            f"This person has a {body_type} body type. "
            "Make the workout tailored to these characteristics."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fitness coach."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        result = response['choices'][0]['message']['content'].strip()

        return JsonResponse({'workout': result})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def generate_diet(request):
    if request.method == 'POST':
        body_type = request.POST.get('body_type')
        goal = request.POST.get('goal')
        diet_preference = request.POST.get('diet_preference')

        prompt = (
            f"Create a balanced {diet_preference} diet plan for someone whose goal is to {goal}. "
            f"This person has a {body_type} body type. Ensure the diet supports their health and goals."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a nutritionist."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        result = response['choices'][0]['message']['content'].strip()

        return JsonResponse({'diet': result})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def nutritionix(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        food = request.POST.get('food')

        headers = {
            "x-app-id": os.getenv("NUTRITIONIX_APP_ID"),
            "x-app-key": os.getenv("NUTRITIONIX_APP_KEY"),
            "x-remote-user-id": "0"
        }

        if query:
            url = "https://trackapi.nutritionix.com/v2/search/instant"
            params = {"query": query}
            r = requests.get(url, headers=headers, params=params)
            if r.status_code == 200:
                data = r.json()
                suggestions = [item["food_name"] for item in data.get("common", [])]
                return JsonResponse({"suggestions": suggestions})
            else:
                return JsonResponse({"error": "Nutritionix API error"}, status=r.status_code)

        elif food:
            url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
            payload = {"query": food}
            r = requests.post(url, headers=headers, json=payload)
            if r.status_code == 200:
                data = r.json()
                calories = sum(item.get("nf_calories", 0) for item in data.get("foods", []))
                fat = sum(item.get("nf_total_fat", 0) for item in data.get("foods", []))
                protein = sum(item.get("nf_protein", 0) for item in data.get("foods", []))
                carbohydrates = sum(item.get("nf_total_carbohydrate", 0) for item in data.get("foods", []))
                fiber = sum(item.get("nf_dietary_fiber", 0) for item in data.get("foods", []))
                result = {
                    "Calories": calories,
                    "Fat": fat,
                    "Protein": protein,
                    "Carbohydrates": carbohydrates,
                    "Fiber": fiber,
                }
                return JsonResponse(result)
            else:
                return JsonResponse({"error": "Nutritionix API error"}, status=r.status_code)
        else:
            return JsonResponse({"error": "Missing query or food parameter"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)
