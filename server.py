import asyncio
import json
import logging
import urllib.request
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agent import Agent, serialize_tasks
from config import load_config
from memory.conversation import Conversation
from memory.task import get_task_store
from prompts import build_system_prompt, list_profiles
from utils.enums import Command, EventType, Role
from utils.log import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

config = load_config()

app = FastAPI()

static_dir = Path("static/assets")
if static_dir.is_dir():
    app.mount(
        "/assets", StaticFiles(directory=static_dir), name="assets"
    )


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


def _convert_messages(messages: list[dict]) -> list[dict]:
    result: list[dict] = []
    tool_call_map: dict[str, dict] = {}

    for msg in messages:
        role = msg.get("role")

        if role == Role.SYSTEM:
            continue

        if role == Role.USER:
            result.append(
                {"role": Role.USER, "content": msg["content"]}
            )

        elif role == Role.ASSISTANT:
            tool_calls_raw = msg.get("tool_calls", [])
            if tool_calls_raw:
                calls = []
                for tc in tool_calls_raw:
                    fn = tc.get("function", {})
                    name = fn.get("name", "")
                    try:
                        args = json.loads(
                            fn.get("arguments", "{}")
                        )
                    except json.JSONDecodeError:
                        args = {}
                    call = {"name": name, "args": args}
                    calls.append(call)
                    tool_call_map[tc["id"]] = call

                result.append({"role": Role.TOOL, "calls": calls})

            content = msg.get("content")
            if content:
                result.append(
                    {"role": Role.ASSISTANT, "content": content}
                )

        elif role == Role.TOOL:
            tc_id = msg.get("tool_call_id")
            if tc_id and tc_id in tool_call_map:
                tool_call_map[tc_id]["result"] = msg.get(
                    "content", ""
                )

    return result


@app.get("/api/history")
async def history() -> dict:
    system_prompt = build_system_prompt()
    conversation = Conversation.load(system_prompt)
    tasks = serialize_tasks(get_task_store().list_all())
    return {
        "messages": _convert_messages(conversation.messages),
        "tasks": tasks,
    }


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    logger.info("WebSocket connected")
    system_prompt = build_system_prompt()
    conversation = Conversation.load(system_prompt)
    agent = Agent(config, conversation)

    try:
        while True:
            data = await ws.receive_json()
            message = data.get("message", "")

            if not message:
                continue

            if message.lower() == Command.CLEAR:
                Conversation.clear_history()
                get_task_store().clear()
                conversation = Conversation(system_prompt)
                agent = Agent(config, conversation)
                await ws.send_json(
                    {"type": EventType.CLEARED}
                )
                continue

            if message.lower().startswith(Command.MODE):
                parts = message.split(maxsplit=1)
                if len(parts) < 2:
                    available = ", ".join(list_profiles())
                    await ws.send_json({
                        "type": EventType.SYSTEM_MESSAGE,
                        "content": f"Available: {available}",
                    })
                    continue
                profile_name = parts[1].strip().lower()
                if profile_name not in list_profiles():
                    available = ", ".join(list_profiles())
                    await ws.send_json({
                        "type": EventType.SYSTEM_MESSAGE,
                        "content": f"Unknown profile"
                        f" '{profile_name}'."
                        f" Available: {available}",
                    })
                    continue
                system_prompt = build_system_prompt(
                    profile_name
                )
                conversation = Conversation(system_prompt)
                agent = Agent(config, conversation)
                await ws.send_json({
                    "type": EventType.SYSTEM_MESSAGE,
                    "content": f"Switched to"
                    f" {profile_name} mode.",
                })
                continue

            for event in agent.run(message):
                await ws.send_json(event)
                await asyncio.sleep(0)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        conversation.save()
