from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, chatbot_api_view, store_message, chatbot_stream_view, get_messages_by_session

router = DefaultRouter()
router.register(r'', ChatSessionViewSet, basename='chatapp')

urlpatterns = [
    path('chatbot/', chatbot_api_view, name='chatbot'),
    path('store_message/', store_message, name='store_message'),
    path("<uuid:session_id>/messages/", get_messages_by_session, name="get_messages_by_session"),

    # path("chatbot/stream/", chatbot_stream_view, name="chatbot-stream"),
    path('', include(router.urls)),  # adds /api/chatapp/ endpoints
]
