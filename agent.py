"""
Phase 3 puis Phase 4 — remplacer le routeur code a la main par le LLM.

Phase 3 : le LLM repond en JSON, Python fait le pont a la main vers vos
fonctions de tools.py.

Phase 4 : la vraie boucle agentique, avec le "function calling" natif de
l'API Groq (compatible OpenAI) a la place du JSON fait main.
"""
import os
import json

from dotenv import load_dotenv
from groq import Groq

from tools import get_course, get_room, get_teacher, send_reminder

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

TOOLS_BY_NAME = {
    "get_course": get_course,
    "get_room": get_room,
    "get_teacher": get_teacher,
    "send_reminder": send_reminder,
}

# ---------------------------------------------------------------------------
# Phase 3 — le LLM repond en JSON, Python parse ce JSON a la main
# ---------------------------------------------------------------------------

JSON_BRIDGE_PROMPT = """Tu es un assistant qui choisit un outil a appeler.
Outils disponibles :
- get_course(course_name)
- get_room(course_name)
- get_teacher(course_name)
- send_reminder(message)

Reponds UNIQUEMENT avec un objet JSON de cette forme, sans texte autour :
{"tool": "nom_de_l_outil", "arguments": {"...": "..."}}
"""


def ask_llm_for_tool_json(question: str) -> dict:
    """Exercice Phase 3 — TODO :

    1. Appelez client.chat.completions.create avec model=MODEL et deux
       messages : un message "system" = JSON_BRIDGE_PROMPT, un message
       "user" = question.
    2. Recuperez le texte de la reponse (response.choices[0].message.content).
    3. Transformez ce texte en dictionnaire Python avec json.loads() et
       renvoyez-le.
    """
    raise NotImplementedError("A vous de jouer : Phase 3")


def call_tool_from_json(decision: dict):
    """Deja fourni : execute la fonction designee par `decision` avec ses
    arguments. C'est le pont entre le JSON renvoye par le LLM et vos
    fonctions Python de tools.py.
    """
    tool_fn = TOOLS_BY_NAME[decision["tool"]]
    return tool_fn(**decision["arguments"])


# ---------------------------------------------------------------------------
# Phase 4 — la boucle agentique avec le function calling natif de Groq
# ---------------------------------------------------------------------------

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_course",
            "description": "Renvoie l'heure, la salle et l'enseignant d'un cours.",
            "parameters": {
                "type": "object",
                "properties": {"course_name": {"type": "string"}},
                "required": ["course_name"],
            },
        },
    },
    # TODO : ajoutez les schemas de get_room, get_teacher et send_reminder,
    # sur le meme modele que get_course ci-dessus.
]


def run_agent(question: str, max_steps: int = 5) -> str:
    """Exercice Phase 4 — TODO : la boucle agentique complete.

    1. Construisez `messages` avec un seul message {"role": "user",
       "content": question}.
    2. Appelez client.chat.completions.create(model=MODEL, messages=messages,
       tools=TOOLS_SCHEMA) et recuperez `message = response.choices[0].message`.
    3. Si message.tool_calls est vide : la reponse est terminee, renvoyez
       message.content.
    4. Sinon : ajoutez `message` a `messages`, puis pour chaque tool_call,
       executez la fonction correspondante (TOOLS_BY_NAME + json.loads sur
       tool_call.function.arguments) et ajoutez a `messages` un message
       {"role": "tool", "tool_call_id": tool_call.id, "content": ...}
       avec le resultat converti en texte (json.dumps).
    5. Repetez depuis l'etape 2, jusqu'a max_steps tours maximum pour
       eviter une boucle infinie.
    """
    raise NotImplementedError("A vous de jouer : Phase 4")


if __name__ == "__main__":
    print(run_agent("Dans quelle salle est le cours de Docker ?"))
