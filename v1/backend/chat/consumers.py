import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from langchain_pipeline.langraph_pipeline import LangGraphPipeline

logging.basicConfig(level=logging.INFO)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection."""
        await self.accept()
        logging.info("🔗 WebSocket connection established.")

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        logging.info("🔴 WebSocket disconnected.")

    async def receive(self, text_data):
        """Processes messages received from WebSocket client."""
        data = json.loads(text_data)
        user_message = data.get("user_message", "")
        use_agent = data.get("use_agent", False)

        logging.info(f"📩 Received message: {user_message}")

        if user_message.lower() == "exit":
            await self.send(text_data=json.dumps({"response": "Goodbye! Closing connection."}))
            await self.close()
            return

        # ✅ Process message with LangChain
        pipeline = LangGraphPipeline()
        response = pipeline.run_pipeline(user_message, use_agent)

        await self.send(text_data=json.dumps({"response": response}))
