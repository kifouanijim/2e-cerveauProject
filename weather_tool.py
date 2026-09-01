import json
from datetime import datetime
from urllib import request, parse

PARIS_LATITUDE = 48.8566
PARIS_LONGITUDE = 2.3522


def _weather_description(code: int) -> str:
    mapping = {
        0: "ciel dégagé",
        1: "peu nuageux",
        2: "partiellement nuageux",
        3: "couvert",
        45: "brouillard",
        48: "brouillard givrant",
        51: "bruine légère",
        53: "bruine modérée",
        55: "bruine forte",
        56: "bruine verglaçante légère",
        57: "bruine verglaçante forte",
        61: "pluie faible",
        63: "pluie modérée",
        65: "pluie forte",
        66: "pluie verglaçante",
        67: "pluie verglaçante forte",
        71: "neige légère",
        73: "neige modérée",
        75: "neige forte",
        77: "grésil",
        80: "averses faibles",
        81: "averses modérées",
        82: "averses fortes",
        85: "averses de neige faibles",
        86: "averses de neige fortes",
        95: "orage",
        96: "orage avec grêle",
        99: "orage avec grêle intense",
    }
    return mapping.get(code, "conditions variables")


def _resolve_day_index(day: str) -> int:
    normalized = (day or "").lower().replace("é", "e").replace("è", "e")
    if "demain" in normalized or "tomorrow" in normalized:
        return 1
    if "aujourd" in normalized or "today" in normalized:
        return 0
    return 1


def get_weather(day: str):
    """Retourne une phrase décrivant la météo prévue à Paris pour le jour demandé."""
    index = _resolve_day_index(day)
    params = {
        "latitude": PARIS_LATITUDE,
        "longitude": PARIS_LONGITUDE,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "Europe/London",
        "forecast_days": 3,
    }
    url = "https://api.open-meteo.com/v1/forecast?" + parse.urlencode({k: v for k, v in params.items()})

    with request.urlopen(url, timeout=20) as response:
        payload = json.load(response)

    daily = payload.get("daily", {})
    dates = daily.get("time", [])
    weather_codes = daily.get("weather_code", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])

    if not dates:
        return "Je n'ai pas accès aux prévisions météo pour Paris pour le moment."

    if index >= len(dates):
        index = len(dates) - 1

    date_label = dates[index]
    code = weather_codes[index] if index < len(weather_codes) else 0
    max_temp = max_temps[index] if index < len(max_temps) else None
    min_temp = min_temps[index] if index < len(min_temps) else None
    description = _weather_description(code)

    if day and ("demain" in day.lower() or "tomorrow" in day.lower()):
        label = "demain"
    else:
        label = "aujourd'hui"

    if max_temp is not None and min_temp is not None:
        return (
            f"À Paris, {label} ({date_label}), le temps est {description} "
            f"avec un maximum de {max_temp}°C et un minimum de {min_temp}°C."
        )
    return f"À Paris, {label} ({date_label}), le temps est {description}."


if __name__ == "__main__":
    print(get_weather("demain"))
