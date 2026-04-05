import asyncio
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agent import create_agent
from config import load_config
from memory.conversation import Conversation
from prompts import build_system_prompt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

config = load_config()
run_agent = create_agent(config)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    logger.info("WebSocket connected")
    conversation = Conversation.load(build_system_prompt())

    try:
        while True:
            data = await ws.receive_json()
            message = data.get("message", "")

            if not message:
                continue

            if message.lower() == "/clear":
                Conversation.clear_history()
                conversation = Conversation(build_system_prompt())
                await ws.send_json({"type": "cleared"})
                continue

            for event in run_agent(conversation, message):
                await ws.send_json(event)
                await asyncio.sleep(0)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        conversation.save()
