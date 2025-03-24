from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from langchain_pipeline.langraph_pipeline import LangGraphPipeline
import logging
import uvicorn
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

app = FastAPI()
pipeline = LangGraphPipeline()

class ChatRequest(BaseModel):
    user_message: str
    use_agent: bool = True  # Default to not using the agent

@app.get("/")
async def root():
    """Root endpoint to handle 404 errors."""
    return {"message": "Welcome to the RAG chatbot API!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for a continuous chat session.
    """
    await websocket.accept()
    logging.info("🔗 WebSocket connection established.")

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("user_message", "")
            use_agent = data.get("use_agent", True)

            logging.info(f"📩 Received message: {user_message}")

            if user_message.lower() == "exit":
                await websocket.send_json({"response": "Goodbye! Closing connection."})
                await websocket.close()
                logging.info("🔴 WebSocket connection closed.")
                break

            response = pipeline.run_pipeline(user_message, False)
            await websocket.send_json({"response": response})  # ✅ Ensure message is sent immediately

    except Exception as e:
        logging.error(f"🚨 WebSocket Error: {str(e)}")
        await websocket.close()

# ✅ Ensure FastAPI starts when running main.py
if __name__ == "__main__":
    load_dotenv()
    logging.info("🚀 Starting FastAPI WebSocket Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
