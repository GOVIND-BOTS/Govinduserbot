"""ICC Gemini agent with explicit confirmation for Telegram actions."""
import asyncio
import os
import secrets
from datetime import datetime, timedelta

from pyrogram import Client, filters
from ICC.modules.help import add_command_help

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

MODEL = os.getenv("GEMINI_AGENT_MODEL", "gemini-3.7-flash")
INTENT_MODEL = os.getenv("GEMINI_INTENT_MODEL", "gemini-flash-lite-latest")
TTL = 120
PENDING = {}
INTENTS = {}

SAFE = [
    {"name": "search_messages", "description": "Search messages in the current chat.",
     "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}, "limit": {"type": "INTEGER"}}, "required": ["query"]}},
    {"name": "get_recent_messages", "description": "Read recent messages in the current chat.",
     "parameters": {"type": "OBJECT", "properties": {"limit": {"type": "INTEGER"}}}},
]
RISKY = [
    {"name": "send_message_to_chat", "description": "Queue sending a message to another chat. Confirmation required.",
     "parameters": {"type": "OBJECT", "properties": {"chat": {"type": "STRING"}, "text": {"type": "STRING"}}, "required": ["chat", "text"]}},
    {"name": "join_group", "description": "Queue joining a group or channel. Confirmation required.",
     "parameters": {"type": "OBJECT", "properties": {"chat": {"type": "STRING"}}, "required": ["chat"]}},
    {"name": "leave_group", "description": "Queue leaving a group or channel. Confirmation required.",
     "parameters": {"type": "OBJECT", "properties": {"chat": {"type": "STRING"}}, "required": ["chat"]}},
    {"name": "delete_messages", "description": "Queue deleting message IDs. Confirmation required.",
     "parameters": {"type": "OBJECT", "properties": {"chat": {"type": "STRING"}, "message_ids": {"type": "ARRAY", "items": {"type": "INTEGER"}}}, "required": ["chat", "message_ids"]}},
    {"name": "forward_message", "description": "Queue forwarding a message. Confirmation required.",
     "parameters": {"type": "OBJECT", "properties": {"from_chat": {"type": "STRING"}, "message_id": {"type": "INTEGER"}, "to_chat": {"type": "STRING"}}, "required": ["from_chat", "message_id", "to_chat"]}},
]
RISKY_NAMES = {item["name"] for item in RISKY}
TOOLS = [types.Tool(function_declarations=SAFE + RISKY)] if types else None


def describe(name, args):
    if name == "send_message_to_chat":
        return "Send message to {}: {}".format(args.get("chat"), str(args.get("text", ""))[:160])
    if name == "join_group":
        return "Join {}".format(args.get("chat"))
    if name == "leave_group":
        return "Leave {}".format(args.get("chat"))
    if name == "delete_messages":
        return "Delete IDs {} in {}".format(args.get("message_ids"), args.get("chat"))
    if name == "forward_message":
        return "Forward message {} to {}".format(args.get("message_id"), args.get("to_chat"))
    return name


async def gemini_client():
    if genai is None:
        raise RuntimeError("google-genai package missing; install requirements.txt.")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in hosting environment variables.")
    return genai.Client(api_key=key)


async def understand(task):
    try:
        ai = await gemini_client()
        result = await ai.aio.models.generate_content(
            model=INTENT_MODEL,
            contents="Restate this task in 1-2 sentences. Do not perform it. Match the user's language:\\n\\n" + task,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=150),
        )
        return (result.text or task).strip()
    except Exception:
        return task


async def read_chat(client, chat_id, limit=20, query=None):
    limit = max(1, min(int(limit or 20), 50))
    iterator = client.search_messages(chat_id, query, limit=limit) if query else client.get_chat_history(chat_id, limit=limit)
    found = []
    async for msg in iterator:
        body = msg.text or msg.caption
        if body:
            user = msg.from_user
            name = (user.first_name if user else None) or (user.username if user else None) or "Unknown"
            found.append({"id": msg.id, "sender": name, "text": body[:300], "date": str(msg.date)})
    return {"status": "ok", "count": len(found), "messages": found}


def queue_action(chat_id, name, args):
    action_id = secrets.token_hex(3)
    PENDING[action_id] = {
        "chat_id": chat_id, "name": name, "args": args,
        "description": describe(name, args),
        "expires": datetime.now() + timedelta(seconds=TTL),
    }
    return action_id


async def execute_action(client, name, args):
    try:
        if name == "send_message_to_chat":
            await client.send_message(args["chat"], str(args["text"])[:4000])
            return "Message sent."
        if name == "join_group":
            await client.join_chat(args["chat"])
            return "Joined."
        if name == "leave_group":
            await client.leave_chat(args["chat"])
            return "Left."
        if name == "delete_messages":
            ids = [int(value) for value in args["message_ids"]][:50]
            if not ids:
                return "No message IDs supplied."
            await client.delete_messages(args["chat"], ids)
            return "Deleted {} message(s).".format(len(ids))
        if name == "forward_message":
            await client.forward_messages(args["to_chat"], args["from_chat"], int(args["message_id"]))
            return "Forwarded."
        return "Unknown action."
    except Exception as exc:
        return "Failed: {}".format(str(exc)[:220])


async def run_agent(client, chat_id, task):
    ai = await gemini_client()
    history = [types.Content(role="user", parts=[types.Part(text=task)])]
    queued = []
    for _ in range(5):
        response = await ai.aio.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction="You are ICC AI Agent. Read only the current chat with safe tools. "
                "Actions involving another chat, group membership, deletion or forwarding must be queued "
                "for explicit confirmation. Never claim a queued action has been executed.",
                tools=TOOLS, temperature=0.2, max_output_tokens=1200,
            ),
        )
        candidate = response.candidates[0] if response.candidates else None
        parts = candidate.content.parts if candidate and candidate.content else []
        calls = [part.function_call for part in parts if getattr(part, "function_call", None)]
        if not calls:
            answer = response.text or "No response from Gemini."
            if queued:
                answer += "\\n\\nQueued, not executed: " + ", ".join(queued)
                answer += "\\nReview with .pending, then use .confirm ID or .cancel ID."
            return answer

        history.append(candidate.content)
        tool_results = []
        risky_queued = False
        for call in calls:
            args = dict(call.args or {})
            if call.name in RISKY_NAMES:
                action_id = queue_action(chat_id, call.name, args)
                queued.append(action_id)
                result = {"status": "queued_for_confirmation", "action_id": action_id}
                risky_queued = True
            elif call.name == "search_messages":
                query = str(args.get("query", "")).strip()
                result = await read_chat(client, chat_id, args.get("limit", 20), query) if query else {"status": "error", "message": "Empty query"}
            elif call.name == "get_recent_messages":
                result = await read_chat(client, chat_id, args.get("limit", 20))
            else:
                result = {"status": "error", "message": "Unknown tool"}
            tool_results.append(types.Part.from_function_response(name=call.name, response=result))
        history.append(types.Content(role="user", parts=tool_results))
        if risky_queued:
            return "Requested action queued for your review. It has NOT been executed. IDs: " + ", ".join(queued) + ". Use .pending, then .confirm ID or .cancel ID."
    return "Agent reached its step limit. Try a smaller task."


@Client.on_message(filters.command("agent", ".") & filters.me)
async def agent_handler(client, message):
    task = " ".join(message.command[1:]).strip()
    if not task:
        return await message.edit_text("ICC AI Agent\\nUsage: .agent <task>\\nExample: .agent summarize the recent messages in this chat")
    status = await message.edit_text("Understanding your task...")
    summary = await understand(task)
    INTENTS[message.chat.id] = {"task": task, "prompt_id": status.id, "expires": datetime.now() + timedelta(seconds=TTL)}
    await status.edit_text("I understood:\\n" + summary + "\\n\\nReply haan/nahi to this message to continue.")


@Client.on_message(filters.text & filters.me, group=20)
async def intent_reply(client, message):
    pending = INTENTS.get(message.chat.id)
    if not pending or not message.reply_to_message or message.reply_to_message.id != pending["prompt_id"]:
        return
    if not message.text or message.text.startswith("."):
        return
    if datetime.now() > pending["expires"]:
        INTENTS.pop(message.chat.id, None)
        return
    choice = message.text.strip().lower()
    if choice in {"haan", "han", "ha", "yes", "y", "ok", "okay", "👍", "✅"}:
        INTENTS.pop(message.chat.id, None)
        status = await message.reply_text("ICC Agent working...")
        try:
            result = await asyncio.wait_for(run_agent(client, message.chat.id, pending["task"]), timeout=75)
        except asyncio.TimeoutError:
            result = "Agent timed out. Try a smaller task."
        except Exception as exc:
            result = "Agent error: {}".format(str(exc)[:400])
        await status.edit_text(result[:4000])
    elif choice in {"nahi", "na", "no", "n", "cancel", "stop"}:
        INTENTS.pop(message.chat.id, None)
        await message.reply_text("Task cancelled.")


@Client.on_message(filters.command("confirm", ".") & filters.me)
async def confirm_handler(client, message):
    if len(message.command) != 2:
        return await message.edit_text("Usage: .confirm <id>")
    action_id = message.command[1]
    item = PENDING.get(action_id)
    if not item or item["chat_id"] != message.chat.id:
        return await message.edit_text("No matching pending action in this chat.")
    if datetime.now() > item["expires"]:
        PENDING.pop(action_id, None)
        return await message.edit_text("This action expired. Ask the agent again.")
    PENDING.pop(action_id, None)
    status = await message.edit_text("Executing: " + item["description"])
    result = await execute_action(client, item["name"], item["args"])
    await status.edit_text(item["description"] + "\\n\\n" + result)


@Client.on_message(filters.command("cancel", ".") & filters.me)
async def cancel_handler(client, message):
    if len(message.command) != 2:
        return await message.edit_text("Usage: .cancel <id>")
    action_id = message.command[1]
    item = PENDING.get(action_id)
    if not item or item["chat_id"] != message.chat.id:
        return await message.edit_text("No matching pending action in this chat.")
    PENDING.pop(action_id, None)
    await message.edit_text("Cancelled: " + item["description"])


@Client.on_message(filters.command("pending", ".") & filters.me)
async def pending_handler(client, message):
    now = datetime.now()
    for key in list(PENDING):
        if PENDING[key]["expires"] <= now:
            PENDING.pop(key, None)
    items = [(key, value) for key, value in PENDING.items() if value["chat_id"] == message.chat.id]
    if not items:
        return await message.edit_text("No pending actions in this chat.")
    lines = ["{} — {} ({}s left)".format(key, value["description"], max(0, int((value["expires"] - now).total_seconds()))) for key, value in items]
    await message.edit_text("Pending confirmations:\\n\\n" + "\\n".join(lines))


add_command_help("agent", [
    [".agent <task>", "Ask Gemini to inspect the current chat or prepare an action."],
    [".confirm <id>", "Execute a queued action after reviewing it."],
    [".cancel <id>", "Cancel a queued action."],
    [".pending", "List pending actions in this chat."],
])
