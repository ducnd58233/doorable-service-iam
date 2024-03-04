from django.urls import path
from .views import Register

urlpatterns = [
    path("signup", Register.as_view()),
]
