from google.adk.agents import Agent
from google.adk.tools import google_search

# Crear un agente con la herramienta de búsqueda de Google
root_agent = Agent(
    name="InvestigadorGoogle",
    model="gemini-2.5-flash",
    description="Un agente que usa búsqueda de Google para responder preguntas actuales",
    tools=[google_search],  # Herramienta preconstruida
    instruction=(
        "Eres un investigador experto. "
        "Usa la búsqueda de Google para encontrar información actualizada. "
        "Cita tus fuentes cuando sea posible."
    )
)