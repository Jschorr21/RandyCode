"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing  # ✅ Import WebSocket routes

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # ✅ HTTP requests
    "websocket": AuthMiddlewareStack(  # ✅ WebSockets
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
