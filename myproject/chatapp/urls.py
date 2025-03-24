from django.urls import path
from .views import chatbot_api_view, store_message

urlpatterns = [
    path("chatbot/", chatbot_api_view, name="chatbot"),
    path("store_message/", store_message, name="store_message"),  # FastAPI will call this
]
