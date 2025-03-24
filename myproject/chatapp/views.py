from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils.langchain_bridge import get_response_from_pipeline
from .models import ChatSession, Message

@api_view(["POST"])
def chatbot_api_view(request):
    user_message = request.data.get("message")
    if not user_message:
        return Response({"error": "No message provided"}, status=400)
    response = get_response_from_pipeline(user_message)
    return Response({"response": response})

@api_view(["POST"])
def store_message(request):
    data = request.data
    session_id = data.get("session_id")
    user_message = data.get("user_message")
    bot_response = data.get("bot_response")

    session, _ = ChatSession.objects.get_or_create(session_id=session_id)
    Message.objects.create(session=session, sender="user", text=user_message)
    Message.objects.create(session=session, sender="bot", text=bot_response)

    return Response({"status": "stored"})
