import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import requests

def get_weather(city: str) -> dict:
    """Devuelve un reporte de clima usando la API pública wttr.in (sin clave)."""
    response = requests.get(f"https://wttr.in/{city}?format=j1")
    if not response.ok:
        return {"status": "error", "error_message": "No pude obtener el clima."}
    data = response.json()
    c = data["current_condition"][0]
    report = (
        f"El clima en {city} es {c['weatherDesc'][0]['value'].lower()} "
        f"con temperatura {c['temp_C']}°C, humedad {c['humidity']}% "
        f"y sensación térmica {c['FeelsLikeC']}°C."
    )
    return {"status": "success", "report": report}


def get_current_time(city: str) -> dict:
    """Devuelve hora local para múltiples ciudades usando sus zonas horarias."""
    # Diccionario ampliado de ciudades y sus zonas horarias
    tz_map = {
        "bogota": "America/Bogota",
        "nueva york": "America/New_York",
        "londres": "Europe/London",
        "paris": "Europe/Paris",
        "madrid": "Europe/Madrid",
        "tokio": "Asia/Tokyo",
        "sydney": "Australia/Sydney",
        "ciudad de mexico": "America/Mexico_City",
        "buenos aires": "America/Argentina/Buenos_Aires",
        "hong kong": "Asia/Hong_Kong",
        "dubai": "Asia/Dubai",
        "moscú": "Europe/Moscow",
        "singapur": "Asia/Singapore",
        "rio de janeiro": "America/Sao_Paulo",
        "chicago": "America/Chicago",
        "los angeles": "America/Los_Angeles",
        "toronto": "America/Toronto",
        "berlin": "Europe/Berlin",
        "amsterdam": "Europe/Amsterdam",
        "roma": "Europe/Rome"
    }
    # Normalizar la entrada
    city_lower = city.lower()

    if city_lower not in tz_map:
        return {"status": "error", "error_message": f"No tengo zona horaria para {city}."}

    try:
        now = datetime.datetime.now(ZoneInfo(tz_map[city_lower]))
        report = now.strftime("%H:%M:%S del %d-%m-%Y")
        return {"status": "success", "report": f"La hora en {city} es {report}."}
    except Exception as e:
        return {"status": "error", "error_message": f"Error al obtener la hora: {str(e)}"}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description=(
        "Eres un agente que responde preguntas sobre el clima y la hora"
    ),
    instruction=(
        "Eres un asistente que puede responder preguntas del clima y la hora de acuerdo a la ciudad, usa las herramientas disponibles para ello"
        "Envia la ciudad en minuscula y sin acentos o simbolos, responde siempre en español"

    ),
    tools=[get_weather, get_current_time],
)