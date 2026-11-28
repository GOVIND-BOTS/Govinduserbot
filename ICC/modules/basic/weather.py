import aiohttp
from pyrogram import Client, filters
from ICC.modules.help import add_command_help


WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 56: "Freezing drizzle", 57: "Heavy freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 66: "Freezing rain",
    67: "Heavy freezing rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow",
    77: "Snow grains", 80: "Rain showers", 81: "Heavy showers",
    82: "Violent showers", 85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}


async def _fetch(session, url, params):
    async with session.get(url, params=params) as response:
        data = await response.json(content_type=None)
        if response.status != 200:
            raise RuntimeError(data.get("reason", f"Service returned HTTP {response.status}"))
        return data


async def _weather(city):
    timeout = aiohttp.ClientTimeout(total=18)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        geo = await _fetch(session, "https://geocoding-api.open-meteo.com/v1/search",
                           {"name": city, "count": 1, "language": "en", "format": "json"})
        places = geo.get("results") or []
        if not places:
            raise ValueError("City not found. Check the spelling.")
        place = places[0]
        data = await _fetch(session, "https://api.open-meteo.com/v1/forecast", {
            "latitude": place["latitude"], "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "forecast_days": 3, "timezone": "auto",
        })
    return place, data


@Client.on_message(filters.command(["weather", "w"], ".") & filters.me)
async def get_weather(_, message):
    city = " ".join(message.command[1:]).strip()
    if not city:
        return await message.edit_text("Usage: .weather <city>\nExample: .weather Indore")
    if len(city) > 80:
        return await message.edit_text("City name is too long.")
    status = await message.edit_text("Checking current weather…")
    try:
        place, data = await _weather(city)
        current = data["current"]
        location = ", ".join(x for x in (place.get("name"), place.get("admin1"), place.get("country")) if x)
        condition = WEATHER_CODES.get(current.get("weather_code"), "Unknown")
        result = (
            f"🌤️ **Weather — {location}**\n"
            f"**Condition:** {condition}\n"
            f"**Temperature:** {current.get('temperature_2m')}°C\n"
            f"**Feels like:** {current.get('apparent_temperature')}°C\n"
            f"**Humidity:** {current.get('relative_humidity_2m')}%\n"
            f"**Wind:** {current.get('wind_speed_10m')} km/h\n"
            f"**Rain:** {current.get('precipitation')} mm\n"
            f"**Local time:** {current.get('time')}\n"
            "_Source: Open-Meteo_"
        )
        await status.edit_text(result)
    except Exception as exc:
        await status.edit_text(f"Weather lookup failed: {str(exc)[:250]}")


@Client.on_message(filters.command("forecast", ".") & filters.me)
async def get_forecast(_, message):
    city = " ".join(message.command[1:]).strip()
    if not city:
        return await message.edit_text("Usage: .forecast <city>\nExample: .forecast Mumbai")
    if len(city) > 80:
        return await message.edit_text("City name is too long.")
    status = await message.edit_text("Fetching 3-day forecast…")
    try:
        place, data = await _weather(city)
        daily = data["daily"]
        location = ", ".join(x for x in (place.get("name"), place.get("country")) if x)
        lines = [f"📅 **3-Day Forecast — {location}**"]
        for i, day in enumerate(daily.get("time", [])):
            condition = WEATHER_CODES.get(daily["weather_code"][i], "Unknown")
            lines.append(
                f"\n**{day} — {condition}**\n"
                f"🌡️ {daily['temperature_2m_min'][i]}°C to {daily['temperature_2m_max'][i]}°C"
                f" | 🌧️ Rain chance: {daily['precipitation_probability_max'][i]}%"
            )
        lines.append("\n_Source: Open-Meteo_")
        await status.edit_text("\n".join(lines))
    except Exception as exc:
        await status.edit_text(f"Forecast lookup failed: {str(exc)[:250]}")


add_command_help("weather", [
    [".weather <city>", "Show current temperature, condition, humidity and wind."],
    [".forecast <city>", "Show a 3-day weather forecast."],
])
