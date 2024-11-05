from django.contrib import admin
from django.urls import path
from api.views import generate_workout, generate_diet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generate_workout/', generate_workout),
    path('generate_diet/', generate_diet),
]
