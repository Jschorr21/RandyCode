from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils.langchain_bridge import get_response_from_pipeline
from .models import ChatSession, Message
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .serializers import ChatSessionSerializer, MessageSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatSession
from .serializers import ChatSessionSerializer  # you'll create this below

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, pk=None):
        session = self.get_object()
        messages = session.messages.all().order_by("timestamp")
        return Response(MessageSerializer(messages, many=True).data)

@permission_classes([IsAuthenticated])
@api_view(["POST"])
def chatbot_api_view(request):
    user_message = request.data.get("message")
    if not user_message:
        return Response({"error": "No message provided"}, status=400)
    response = get_response_from_pipeline(user_message)
    return Response({"response": response})

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def store_message(request):
    session_id = request.data.get("session_id")
    user_message = request.data.get("user_message")
    bot_response = request.data.get("bot_response")

    session, _ = ChatSession.objects.get_or_create(session_id=session_id, user=request.user)
    Message.objects.create(session=session, sender="user", text=user_message)
    Message.objects.create(session=session, sender="bot", text=bot_response)

    return Response({"status": "stored"})