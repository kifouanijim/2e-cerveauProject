import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "weather.json"


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


def get_weather(day: str):
    """Retourne la météo disponible localement dans le projet, sans aucune requête réseau."""
    if not DATA_PATH.exists():
        return "Aucune donnée météo locale n'est disponible dans le projet."

    with open(DATA_PATH, encoding="utf-8") as f:
        payload = json.load(f)

    city_data = payload.get("Paris", {})
    label = "demain" if "demain" in (day or "").lower() or "tomorrow" in (day or "").lower() else "aujourd'hui"
    entry = city_data.get(label, city_data.get("aujourd'hui"))

    if entry is None:
        return "Je n'ai pas de prévision météo locale pour cette période."

    code = entry.get("weather_code", 0)
    max_temp = entry.get("temperature_2m_max")
    min_temp = entry.get("temperature_2m_min")
    date_label = entry.get("date", "")
    description = _weather_description(code)

    if max_temp is not None and min_temp is not None:
        return (
            f"À Paris, {label} ({date_label}), le temps est {description} "
            f"avec un maximum de {max_temp}°C et un minimum de {min_temp}°C."
        )
    return f"À Paris, {label} ({date_label}), le temps est {description}."


if __name__ == "__main__":
    print(get_weather("demain"))
