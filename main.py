from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
    return {"message": "Welcome to the RAG chatbot API!"}

@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    """
    WebSocket endpoint for a continuous chat session, scoped by chat_id.
    """
    await websocket.accept()
    logging.info(f"🔗 WebSocket connection established for chat {chat_id}.")

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("user_message", "")
            # use_agent = data.get("use_agent", True)

            logging.info(f"📩 Chat {chat_id} | Received: {user_message}")

            if user_message.lower() == "exit":
                await websocket.send_json({"response": "Goodbye! Closing connection."})
                await websocket.close()
                logging.info(f"🔴 Chat {chat_id} | WebSocket closed.")
                break

            response= pipeline.run_pipeline(user_message, use_agent=False, thread_id=chat_id)
            await websocket.send_json({"response": response})

    except WebSocketDisconnect:
        logging.info(f"🔌 Chat {chat_id} | WebSocket disconnected by client.")
    except Exception as e:
        logging.error(f"🚨 Chat {chat_id} | Error: {str(e)}")
        await websocket.close()

# ✅ Launch server
if __name__ == "__main__":
    load_dotenv()
    logging.info("🚀 Starting FastAPI WebSocket Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
