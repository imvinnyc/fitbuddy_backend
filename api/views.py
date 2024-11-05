from django.http import JsonResponse
import openai
import os
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

        prompt = (f"Create a {duration}-minute {intensity} intensity workout plan for someone whose goal is to {goal}. "
                  f"This person has a {body_type} body type. "
                  "Make the workout tailored to these characteristics.")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a fitness coach."},
                      {"role": "user", "content": prompt}],
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

        prompt = (f"Create a balanced {diet_preference} diet plan for someone whose goal is to {goal}. "
                  f"This person has a {body_type} body type. Ensure the diet supports their health and goals.")

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
