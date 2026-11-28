# Adapted Pyrogram utilities inspired by LEGENDBOT plugins.
# Original project: https://github.com/Officialgovindmp/LEGENDBOT
# Original project license: GNU GPL v3.0. This file is a Pyrogram rewrite.
import ast
import base64
import hashlib
import json
import operator
from datetime import datetime
from urllib.parse import quote, urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


_SAFE_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_SAFE_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_math(node):
    if isinstance(node, ast.Expression):
        return _safe_math(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_BINOPS:
        left, right = _safe_math(node.left), _safe_math(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent is too large.")
        return _SAFE_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_UNARYOPS:
        return _SAFE_UNARYOPS[type(node.op)](_safe_math(node.operand))
    raise ValueError("Only basic arithmetic is supported.")


@Client.on_message(filters.command(["calc"], ".") & filters.me)
async def calculator(_, message: Message):
    expression = " ".join(message.command[1:]).strip()
    if not expression:
        return await message.edit_text("Usage: `.calc 2 + 9 * 3`")
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_math(tree)
        await message.edit_text(
            f"**Expression:** `{expression[:500]}`\n**Result:** `{result}`"
        )
    except Exception as exc:
        await message.edit_text(f"Calculation error: `{type(exc).__name__}: {str(exc)[:250]}`")


@Client.on_message(filters.command(["hash"], ".") & filters.me)
async def text_hash(_, message: Message):
    value = " ".join(message.command[1:])
    if not value and message.reply_to_message:
        value = message.reply_to_message.text or message.reply_to_message.caption or ""
    if not value:
        return await message.edit_text("Reply to text or use `.hash your text`.")
    raw = value.encode("utf-8")
    result = "\n".join(f"**{name.upper()}:** `{hashlib.new(name, raw).hexdigest()}`"
                        for name in ("md5", "sha1", "sha256", "sha512"))
    await message.edit_text(f"**Text:** `{value[:700]}`\n\n{result}")


@Client.on_message(filters.command(["hbase"], ".") & filters.me)
async def base64_tool(_, message: Message):
    if len(message.command) < 3 or message.command[1].lower() not in ("en", "de"):
        return await message.edit_text("Usage: `.hbase en text` or `.hbase de encoded_text`")
    mode = message.command[1].lower()
    value = " ".join(message.command[2:])
    try:
        if mode == "en":
            output = base64.b64encode(value.encode()).decode()
        else:
            output = base64.b64decode(value, validate=True).decode("utf-8")
        await message.edit_text(f"`{output[:3800]}`")
    except Exception as exc:
        await message.edit_text(f"Base64 error: `{type(exc).__name__}`")


@Client.on_message(filters.command(["time", "stime"], ".") & filters.me)
async def timezone_time(_, message: Message):
    zone = " ".join(message.command[1:]).strip() or "Asia/Kolkata"
    try:
        now = datetime.now(ZoneInfo(zone))
    except ZoneInfoNotFoundError:
        return await message.edit_text(
            "Unknown timezone. Example: `.time Asia/Kolkata`"
        )
    await message.edit_text(
        f"**{zone}**\n**Time:** `{now.strftime('%I:%M:%S %p')}`\n"
        f"**Date:** `{now.strftime('%A, %d %B %Y')}`"
    )


@Client.on_message(filters.command(["ud"], ".") & filters.me)
async def urban_dictionary(_, message: Message):
    term = " ".join(message.command[1:]).strip()
    if not term and message.reply_to_message:
        term = message.reply_to_message.text or ""
    if not term:
        return await message.edit_text("Usage: `.ud word`")
    url = "https://api.urbandictionary.com/v0/define?term=" + quote(term)
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                data = await response.json()
        entries = data.get("list") or []
        if not entries:
            return await message.edit_text("No Urban Dictionary definition found.")
        item = entries[0]
        definition = item.get("definition", "").replace("[", "").replace("]", "")
        example = item.get("example", "").replace("[", "").replace("]", "")
        text = f"**{item.get('word', term)}**\n\n**Meaning:**\n{definition}"
        if example:
            text += f"\n\n**Example:**\n{example}"
        await message.edit_text(text[:4000], disable_web_page_preview=True)
    except Exception as exc:
        await message.edit_text(f"Lookup failed: `{type(exc).__name__}`")


async def _get_url_argument(message: Message):
    value = " ".join(message.command[1:]).strip()
    if not value and message.reply_to_message:
        value = message.reply_to_message.text or message.reply_to_message.caption or ""
    return value.strip().split()[0] if value.strip() else ""


@Client.on_message(filters.command(["short"], ".") & filters.me)
async def shorten_url(_, message: Message):
    value = await _get_url_argument(message)
    if not value:
        return await message.edit_text("Usage: `.short https://example.com`")
    if not urlparse(value if "://" in value else "https://" + value).hostname:
        return await message.edit_text("Please provide a valid URL.")
    target = value if "://" in value else "https://" + value
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://da.gd/s", params={"url": target}) as response:
                result = (await response.text()).strip()
        if response.status != 200 or not result.startswith(("http://", "https://")):
            raise ValueError("Shortener returned an invalid response.")
        await message.edit_text(f"**Short URL:** {result}", disable_web_page_preview=True)
    except Exception as exc:
        await message.edit_text(f"URL shortening failed: `{type(exc).__name__}`")


@Client.on_message(filters.command(["unshort"], ".") & filters.me)
async def expand_url(_, message: Message):
    value = await _get_url_argument(message)
    if not value:
        return await message.edit_text("Usage: `.unshort https://short.url/abc`")
    target = value if "://" in value else "https://" + value
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(target, allow_redirects=True) as response:
                final_url = str(response.url)
        await message.edit_text(f"**Original:** {target}\n**Destination:** {final_url}",
                                disable_web_page_preview=True)
    except Exception as exc:
        await message.edit_text(f"URL expansion failed: `{type(exc).__name__}`")


@Client.on_message(filters.command(["dns"], ".") & filters.me)
async def dns_lookup(_, message: Message):
    value = await _get_url_argument(message)
    if not value:
        return await message.edit_text("Usage: `.dns example.com`")
    parsed = urlparse(value if "://" in value else "https://" + value)
    host = parsed.hostname
    if not host:
        return await message.edit_text("Please provide a valid domain.")
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://dns.google/resolve", params={"name": host, "type": "A"}) as response:
                data = await response.json()
        answers = data.get("Answer") or []
        if not answers:
            return await message.edit_text(f"No A records found for `{host}`.")
        records = "\n".join(f"`{item.get('data')}`" for item in answers[:20])
        await message.edit_text(f"**DNS A records for {host}:**\n{records}")
    except Exception as exc:
        await message.edit_text(f"DNS lookup failed: `{type(exc).__name__}`")


@Client.on_message(filters.command(["json"], ".") & filters.me)
async def json_message(_, message: Message):
    target = message.reply_to_message or message
    try:
        output = json.dumps(target.__dict__, default=str, ensure_ascii=False, indent=2)
    except Exception:
        output = json.dumps(target, default=str, ensure_ascii=False, indent=2)
    if len(output) > 3900:
        output = output[:3900] + "\n..."
    await message.edit_text(f"`{output}`")


add_command_help(
    "legend_utils",
    [
        [".calc <expression>", "Safely evaluate basic arithmetic."],
        [".hash <text>", "Generate MD5, SHA1, SHA256 and SHA512 hashes."],
        [".hbase en|de <text>", "Encode or decode Base64."],
        [".time [timezone]", "Show the current time in an IANA timezone."],
        [".ud <word>", "Look up an Urban Dictionary definition."],
        [".short <url>", "Shorten a URL."],
        [".unshort <url>", "Follow redirects and expand a URL."],
        [".dns <domain>", "Look up DNS A records."],
        [".json", "Show JSON data for this or a replied message."],
    ],
)
