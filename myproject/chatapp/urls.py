from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, chatbot_api_view, store_message

router = DefaultRouter()
router.register(r'', ChatSessionViewSet, basename='chatapp')

urlpatterns = [
    path('chatbot/', chatbot_api_view, name='chatbot'),
    path('store_message/', store_message, name='store_message'),
    
    path('', include(router.urls)),  # adds /api/chatapp/ endpoints
]
