import asyncio
import json
import logging
import urllib.request

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agent import create_agent
from config import load_config
from memory.conversation import Conversation
from prompts import build_system_prompt
from utils.log import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

config = load_config()
run_agent = create_agent(config)

app = FastAPI()
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/api/info")
async def info() -> dict:
    context_length = None
    try:
        req = urllib.request.Request(
            f"{config['base_url'].replace('/v1', '')}/api/show",
            data=json.dumps({"name": config["model"]}).encode(),
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            for key, value in data.get("model_info", {}).items():
                if "context_length" in key:
                    context_length = value
                    break
    except Exception:
        pass

    return {"model": config["model"], "context_length": context_length}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    logger.info("WebSocket connected")
    system_prompt = build_system_prompt()
    conversation = Conversation.load(system_prompt)

    try:
        while True:
            data = await ws.receive_json()
            message = data.get("message", "")

            if not message:
                continue

            if message.lower() == "/clear":
                Conversation.clear_history()
                conversation = Conversation(system_prompt)
                await ws.send_json({"type": "cleared"})
                continue

            for event in run_agent(conversation, message):
                await ws.send_json(event)
                await asyncio.sleep(0)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        conversation.save()
