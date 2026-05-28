from __future__ import annotations

from typing import Any

import httpx

from app.services.cache import TTLCache


WEATHER_CODES = {
    0: "Clear",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Cloudy",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Showers",
    82: "Heavy showers",
    95: "Thunderstorm",
}

WEATHER_ICONS = {
    0: "sun",
    1: "sun",
    2: "cloud-sun",
    3: "cloud",
    45: "cloud-fog",
    48: "cloud-fog",
    51: "cloud-drizzle",
    53: "cloud-drizzle",
    55: "cloud-drizzle",
    61: "cloud-rain",
    63: "cloud-rain",
    65: "cloud-rain",
    71: "cloud-snow",
    73: "cloud-snow",
    75: "cloud-snow",
    80: "cloud-rain",
    81: "cloud-rain",
    82: "cloud-rain",
    95: "cloud-lightning",
}


class WeatherService:
    def __init__(self, cache: TTLCache, refresh_seconds: int):
        self.cache = cache
        self.refresh_seconds = refresh_seconds

    async def current_and_forecast(self, settings: dict[str, Any]) -> dict[str, Any]:
        weather = settings["weather"]
        lat = weather.get("latitude")
        lon = weather.get("longitude")
        if not weather["enabled"] or not lat or not lon:
            return {"configured": False, "current": None, "forecast": [], "error": None}

        forecast_days = self._forecast_days(settings)
        cache_key = f"weather:{lat}:{lon}:{weather['temperature_unit']}:{forecast_days}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,apparent_temperature,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "temperature_unit": weather["temperature_unit"],
                "timezone": "auto",
                "forecast_days": forecast_days,
            }
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
                response.raise_for_status()
            payload = response.json()
            unit = payload.get("current_units", {}).get("temperature_2m", "°")
            current = payload.get("current", {})
            daily = payload.get("daily", {})
            result = {
                "configured": True,
                "current": {
                    "label": weather.get("label", "Local Weather"),
                    "temperature": round(current.get("temperature_2m")),
                    "feels_like": round(current.get("apparent_temperature")),
                    "unit": unit,
                    "condition": WEATHER_CODES.get(current.get("weather_code"), "Conditions"),
                    "icon": WEATHER_ICONS.get(current.get("weather_code"), "cloud"),
                },
                "forecast": [
                    {
                        "date": daily["time"][index],
                        "condition": WEATHER_CODES.get(daily["weather_code"][index], "Forecast"),
                        "icon": WEATHER_ICONS.get(daily["weather_code"][index], "cloud"),
                        "high": round(daily["temperature_2m_max"][index]),
                        "low": round(daily["temperature_2m_min"][index]),
                        "unit": unit,
                    }
                    for index in range(min(forecast_days, len(daily.get("time", []))))
                ],
                "error": None,
            }
        except Exception as exc:
            result = {"configured": True, "current": None, "forecast": [], "error": f"Weather unavailable: {exc}"}
        self.cache.set(cache_key, result, self.refresh_seconds)
        return result

    def _forecast_days(self, settings: dict[str, Any]) -> int:
        days = int(settings.get("weather", {}).get("forecast_days", 4) or 4)
        for block in settings.get("block_instances", []):
            if block.get("type") == "weather" and block.get("enabled", False):
                days = max(days, int(block.get("settings", {}).get("forecast_days", days) or days))
        return max(1, min(7, days))
