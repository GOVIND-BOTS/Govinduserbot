import io
import re

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("cur", ".") & filters.me)
async def currency_convert(client: Client, message: Message):
    args = message.command[1:]
    if len(args) != 3:
        return await message.edit_text("Usage: `.cur <amount> <FROM> <TO>` — example: `.cur 10 USD INR`")
    try:
        amount = float(args[0])
        if amount <= 0 or amount > 1e12:
            raise ValueError
    except ValueError:
        return await message.edit_text("Amount must be a positive number.")
    source, target = args[1].upper(), args[2].upper()
    status = await message.edit_text("Converting currency…")
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://api.frankfurter.app/latest", params={"amount": amount, "from": source, "to": target}) as response:
                data = await response.json(content_type=None)
                if response.status != 200:
                    raise RuntimeError(data.get("message", "Currency code not supported."))
        result = data["rates"][target]
        await status.edit_text(f"**Currency conversion**\n`{amount:g} {source}` = **`{result:,.4f} {target}`**\n_Date: {data.get('date', 'latest available')}_")
    except Exception as exc:
        await status.edit_text(f"**Currency error:** `{str(exc)[:300]}`")


@Client.on_message(filters.command("ip", ".") & filters.me)
async def ip_lookup(client: Client, message: Message):
    address = message.text.split(maxsplit=1)[1].strip() if len(message.command) > 1 else ""
    if not address and message.reply_to_message:
        address = message.reply_to_message.text or ""
    if not address:
        return await message.edit_text("Usage: `.ip <IP address or domain>`")
    if len(address) > 253 or not re.fullmatch(r"[A-Za-z0-9.:-]+", address):
        return await message.edit_text("Please provide a valid IP address or hostname.")
    status = await message.edit_text("Looking up IP information…")
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"http://ip-api.com/json/{address}", params={"fields": "status,message,query,country,regionName,city,isp,org,as,timezone"}) as response:
                data = await response.json(content_type=None)
        if data.get("status") != "success":
            raise RuntimeError(data.get("message", "Lookup failed."))
        output = (
            f"**IP:** `{data.get('query')}`\n"
            f"**Location:** {data.get('city', 'N/A')}, {data.get('regionName', 'N/A')}, {data.get('country', 'N/A')}\n"
            f"**ISP:** {data.get('isp', 'N/A')}\n"
            f"**Organization:** {data.get('org', 'N/A')}\n"
            f"**ASN:** {data.get('as', 'N/A')}\n"
            f"**Timezone:** `{data.get('timezone', 'N/A')}`"
        )
        await status.edit_text(output)
    except Exception as exc:
        await status.edit_text(f"**IP lookup error:** `{str(exc)[:300]}`")


@Client.on_message(filters.command("ifsc", ".") & filters.me)
async def ifsc_lookup(client: Client, message: Message):
    code = message.text.split(maxsplit=1)[1].strip().upper() if len(message.command) > 1 else ""
    if not re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", code):
        return await message.edit_text("Usage: `.ifsc <11-character IFSC>`")
    status = await message.edit_text("Fetching bank branch details…")
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://ifsc.razorpay.com/{code}") as response:
                data = await response.json(content_type=None)
                if response.status != 200:
                    raise RuntimeError("IFSC code not found.")
        output = (
            f"**{data.get('BANK', 'Bank')} — {data.get('BRANCH', 'Branch')}**\n"
            f"**IFSC:** `{data.get('IFSC', code)}`\n"
            f"**Address:** {data.get('ADDRESS', 'N/A')}\n"
            f"**City:** {data.get('CITY', 'N/A')}\n"
            f"**District:** {data.get('DISTRICT', 'N/A')}\n"
            f"**State:** {data.get('STATE', 'N/A')}\n"
            f"**MICR:** `{data.get('MICR', 'N/A')}`"
        )
        await status.edit_text(output)
    except Exception as exc:
        await status.edit_text(f"**IFSC lookup error:** `{str(exc)[:300]}`")


@Client.on_message(filters.command("makeqr", ".") & filters.me)
async def make_qr(client: Client, message: Message):
    value = message.text.split(maxsplit=1)[1].strip() if len(message.command) > 1 else ""
    if not value:
        return await message.edit_text("Usage: `.makeqr <text or URL>`")
    if len(value) > 1500:
        return await message.edit_text("QR content is too long (maximum 1500 characters).")
    status = await message.edit_text("Generating QR code…")
    photo = None
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://api.qrserver.com/v1/create-qr-code/", params={"size": "700x700", "data": value}) as response:
                if response.status != 200:
                    raise RuntimeError(f"QR service HTTP {response.status}")
                raw = await response.read()
        photo = io.BytesIO(raw)
        photo.name = "icc_qr.png"
        await client.send_photo(message.chat.id, photo, caption="QR code generated.", reply_to_message_id=message.id)
        await status.delete()
    except Exception as exc:
        await status.edit_text(f"**QR error:** `{str(exc)[:300]}`")
    finally:
        if photo:
            photo.close()


@Client.on_message(filters.command("color", ".") & filters.me)
async def color_info(client: Client, message: Message):
    value = message.text.split(maxsplit=1)[1].strip().lstrip("#") if len(message.command) > 1 else ""
    if not re.fullmatch(r"(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})", value):
        return await message.edit_text("Usage: `.color <HEX>` — example: `.color #FF8800`")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    red, green, blue = (int(value[i:i + 2], 16) for i in (0, 2, 4))
    await message.edit_text(
        f"**Color:** `#{value.upper()}`\n"
        f"**RGB:** `{red}, {green}, {blue}`\n"
        f"**Decimal:** `{int(value, 16)}`"
    )


add_command_help("tools", [
    [".cur <amount> <FROM> <TO>", "Convert currency using the latest available reference rate."],
    [".ip <IP/domain>", "Look up public IP/hostname network and location information."],
    [".ifsc <code>", "Look up Indian bank branch details from an IFSC code."],
    [".makeqr <text>", "Generate a QR code image from text or a URL."],
    [".color <HEX>", "Show RGB and decimal values for a hexadecimal color."],
])
