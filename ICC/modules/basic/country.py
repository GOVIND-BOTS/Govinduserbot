import aiohttp
from urllib.parse import quote
from pyrogram import Client, filters
from ICC.modules.help import add_command_help


@Client.on_message(filters.command(["country", "nation"], ".") & filters.me)
async def country_info(_, message):
    name = " ".join(message.command[1:]).strip()
    if not name:
        return await message.edit_text("Usage: .country <country name>\nExample: .country India")
    if len(name) > 70:
        return await message.edit_text("Country name is too long.")
    status = await message.edit_text("Fetching country information…")
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"https://restcountries.com/v3.1/name/{quote(name)}",
                params={"fields": "name,capital,region,subregion,population,area,currencies,languages,cca2,cca3,timezones"},
            ) as response:
                data = await response.json(content_type=None)
                if response.status != 200 or not isinstance(data, list) or not data:
                    raise ValueError("Country not found. Check the spelling.")
        item = data[0]
        official = item.get("name", {}).get("official", name)
        capitals = ", ".join(item.get("capital", [])) or "N/A"
        currencies = item.get("currencies", {})
        currency_text = ", ".join(
            f"{value.get('name', code)} ({code}, {value.get('symbol', '')})"
            for code, value in currencies.items()
        ) or "N/A"
        languages = ", ".join(item.get("languages", {}).values()) or "N/A"
        timezones = ", ".join(item.get("timezones", [])[:5]) or "N/A"
        output = (
            f"🌍 **{item.get('name', {}).get('common', name)}**\n"
            f"**Official name:** {official}\n"
            f"**Capital:** {capitals}\n"
            f"**Region:** {item.get('region', 'N/A')} — {item.get('subregion', 'N/A')}\n"
            f"**Population:** {item.get('population', 0):,}\n"
            f"**Area:** {item.get('area', 0):,.0f} km²\n"
            f"**Currency:** {currency_text}\n"
            f"**Languages:** {languages}\n"
            f"**Country codes:** {item.get('cca2', 'N/A')} / {item.get('cca3', 'N/A')}\n"
            f"**Time zones:** {timezones}\n"
            "_Source: REST Countries_"
        )
        await status.edit_text(output)
    except Exception as exc:
        await status.edit_text(f"Country lookup failed: {str(exc)[:250]}")


add_command_help("country", [
    [".country <name>", "Show capital, population, currency, languages and more."],
    [".nation <name>", "Alias for .country."],
])
