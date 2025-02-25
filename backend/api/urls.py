from django.urls import path
from .views import process_message, frontend_view

urlpatterns = [
    path("", frontend_view, name="frontend"),  # ✅ Root URL
    path("chat/", process_message, name="process_message"),
]
