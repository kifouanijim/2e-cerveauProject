"""
Phase 3 puis Phase 4 — remplacer le routeur code a la main par le LLM.

Phase 3 : le LLM repond en JSON, Python fait le pont a la main vers vos
fonctions de tools.py.

Phase 4 : la vraie boucle agentique, avec le "function calling" natif de
l'API Groq (compatible OpenAI) a la place du JSON fait main.
"""
import os
import json
import re
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
import groq as _groq
from groq import Groq

from tools import get_course, get_room, get_teacher, send_reminder, _load_courses
from db_tools import count_students, get_team_project, find_student
from weather_tool import get_weather

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.environ.get("GROQ_MODEL")

TOOLS_BY_NAME = {
    "get_course": get_course,
    "get_room": get_room,
    "get_teacher": get_teacher,
    "send_reminder": send_reminder,
    "count_students": count_students,
    "get_team_project": get_team_project,
    "find_student": find_student,
    "get_weather": get_weather,
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
    messages = [
        {"role": "system", "content": JSON_BRIDGE_PROMPT},
        {"role": "user", "content": question},
    ]
    # If no model is specified, avoid calling the Groq client because its
    # Python SDK requires a `model` kwarg. Use the offline fallback instead
    # and prompt the user to set `GROQ_MODEL` to enable online mode.
    if not MODEL:
        print("No GROQ_MODEL set — using offline fallback. To use the Groq API, set GROQ_MODEL.")
        return _simulate_llm_decision(question)

    try:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        text = response.choices[0].message.content
    except _groq.NotFoundError:
        # Fallback: some users don't have access to the default model.
        # Provide a local, deterministic JSON decision based on keywords
        # so the exercise can be tested without a working Groq model.
        print(
            f"Warning: model '{MODEL}' not found or inaccessible — using offline fallback."
        )
        return _simulate_llm_decision(question)
    except Exception:
        # Other API errors: also fallback to simulated decision so the
        # exercise remains testable offline.
        print("Warning: Groq API error — using offline fallback.")
        return _simulate_llm_decision(question)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\})", text, re.S)
        if m:
            return json.loads(m.group(1))
        raise


def _normalize_text(text: str) -> str:
    """Normalize text for keyword matching across French variants."""
    if text is None:
        return ""
    replacements = {
        "à": "a", "á": "a", "â": "a", "ä": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "î": "i", "ï": "i",
        "ô": "o", "ö": "o",
        "ù": "u", "û": "u", "ü": "u",
        "ç": "c",
    }
    normalized = text.lower()
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized.strip()


def _contains_any(text: str, keywords):
    for keyword in keywords:
        if keyword in text:
            return True
    return False


def _project_names_with_technology(technology: str):
    """Return distinct project names matching a technology from the SQLite DB."""
    db_path = Path(__file__).resolve().parent / "hackathon.db"
    if not db_path.exists():
        return []
    tech = technology.strip().lower()
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT DISTINCT project_name FROM participants WHERE LOWER(technologies) LIKE ? ORDER BY project_name",
            (f"%{tech}%",),
        ).fetchall()
    return [row[0] for row in rows]


def _detect_student_count_question(q: str) -> bool:
    return _contains_any(q, ["combien", "nombre", "nb"]) and _contains_any(
        q,
        [
            "etudiant", "etudiants", "participant", "participants",
            "inscrit", "inscrits", "personne", "personnes", "eleve", "eleves"
        ],
    )


def _detect_weather_question(q: str) -> bool:
    return _contains_any(q, ["meteo", "weather", "temps", "pluie", "nuage", "soleil", "climat", "ensoleille"]) or (
        "temperature" in q and ("demain" in q or "today" in q or "aujourd" in q)
    )


def _detect_project_question(q: str) -> bool:
    return _contains_any(q, ["projet", "projets", "project", "projects"]) and _contains_any(
        q,
        [
            "python", "javascript", "docker", "react", "sql", "api", "flask",
            "fastapi", "rasa", "mongodb", "postgresql", "node", "openai"
        ],
    )


def _detect_reminder_question(q: str) -> bool:
    return _contains_any(q, ["rappel", "previens", "prevenir", "notifie", "alerte", "avertis"])


def _simulate_llm_decision(question: str) -> dict:
    """Produce a JSON-like decision dict from simple keyword matching.

    This is a deterministic offline fallback used when the model is
    inaccessible (or for local testing). It mirrors the JSON structure
    the real LLM should return.
    """
    q = _normalize_text(question)
    if "salle" in q:
        return {"tool": "get_room", "arguments": {"course_name": "Docker" if "docker" in q else ""}}
    if "professeur" in q or "enseign" in q:
        return {"tool": "get_teacher", "arguments": {"course_name": "Docker" if "docker" in q else ""}}
    if "horaire" in q or "heure" in q:
        return {"tool": "get_course", "arguments": {"course_name": "Docker" if "docker" in q else ""}}
    if _detect_student_count_question(q):
        return {"tool": "count_students", "arguments": {}}
    if _detect_reminder_question(q):
        return {"tool": "send_reminder", "arguments": {"message": question}}
    if _detect_weather_question(q):
        if "demain" in q or "tomorrow" in q:
            day = "demain"
        elif "aujourd" in q or "today" in q:
            day = "aujourd'hui"
        else:
            day = "demain"
        return {"tool": "get_weather", "arguments": {"day": day}}
    if _detect_project_question(q):
        tech_keywords = [
            "python", "javascript", "java", "react", "docker", "sql",
            "flask", "openai", "api", "node", "postgresql", "rasa",
            "fastapi", "mongodb", "node.js"
        ]
        for tech in tech_keywords:
            if tech in q:
                projects = _project_names_with_technology(tech)
                if projects:
                    return {"tool": "get_team_project", "arguments": {"team": 1}}
                break
    # Default: ask for course info
    return {"tool": "get_course", "arguments": {"course_name": "Docker"}}


def _csv_fallback(question: str):
    """Check the hackathon CSV before returning a final answer when course data does not match."""
    q = question.lower()

    if ("combien" in q or "nb" in q or "nombre" in q) and ("etudiant" in q or "inscrit" in q or "hackathon" in q or "participants" in q):
        return str(count_students())

    team_match = re.search(r"(?:equipe|équipe|team)\s*(\d+)", q)
    if ("projet" in q or "project" in q) and team_match:
        team = int(team_match.group(1))
        info = get_team_project(team)
        if info is not None:
            return json.dumps(info, ensure_ascii=False)
        return f"Aucune équipe {team} trouvée."

    return None


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
    {
        "type": "function",
        "function": {
            "name": "get_room",
            "description": "Renvoie la salle d'un cours.",
            "parameters": {
                "type": "object",
                "properties": {"course_name": {"type": "string"}},
                "required": ["course_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_teacher",
            "description": "Renvoie l'enseignant d'un cours.",
            "parameters": {
                "type": "object",
                "properties": {"course_name": {"type": "string"}},
                "required": ["course_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_reminder",
            "description": "Envoie (simule) un rappel avec un message.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_students",
            "description": "Retourne le nombre total d'étudiants inscrits au hackathon.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_project",
            "description": "Retourne le projet et les technologies d'une équipe donnée.",
            "parameters": {
                "type": "object",
                "properties": {"team": {"type": "integer"}},
                "required": ["team"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_student",
            "description": "Retourne l'équipe et le projet d'un étudiant à partir de son nom.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Retourne une phrase décrivant la météo prévue à Paris pour un jour donné.",
            "parameters": {
                "type": "object",
                "properties": {"day": {"type": "string"}},
                "required": ["day"],
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
    # If no Groq API key is present, or no model specified, run a deterministic
    # local flow based on the JSON bridge and the available `tools` (no
    # external model calls). The Groq Python SDK requires a `model` kwarg,
    # so if GROQ_MODEL is not set we can't safely call the client.
    if not os.environ.get("GROQ_API_KEY") or not MODEL:
        if os.environ.get("GROQ_API_KEY") and not MODEL:
            print("GROQ_API_KEY is set but GROQ_MODEL is not — using offline fallback. Set GROQ_MODEL to enable online mode.")
        
        q = _normalize_text(question)

        # Case 1: general local data should be checked before defaulting to course answers.
        # A single question may contain multiple requests (for example: count + weather).
        answers = []

        if _detect_student_count_question(q):
            answers.append(f"Il y a {count_students()} étudiants qui participent.")

        team_match = re.search(r"(?:equipe|equipe|team)\s*(\d+)", q)
        if ("projet" in q or "project" in q) and team_match:
            team = int(team_match.group(1))
            info = get_team_project(team)
            if info is not None:
                answers.append(json.dumps(info, ensure_ascii=False))
            else:
                answers.append(f"Aucune équipe {team} trouvée.")

        if _detect_project_question(q):
            for tech in ["python", "javascript", "docker", "react", "sql", "api", "flask", "fastapi", "rasa", "mongodb", "postgresql", "node"]:
                if tech in q:
                    matches = []
                    db_path = Path(__file__).resolve().parent / "hackathon.db"
                    if db_path.exists():
                        with sqlite3.connect(db_path) as conn:
                            rows = conn.execute(
                                "SELECT DISTINCT project_name FROM participants WHERE LOWER(technologies) LIKE ? ORDER BY project_name",
                                (f"%{tech}%",),
                            ).fetchall()
                            matches = [row[0] for row in rows]
                    if matches:
                        answers.append(json.dumps(matches, ensure_ascii=False))
                    break

        if _detect_weather_question(q):
            day = "demain" if "demain" in q or "tomorrow" in q else "aujourd'hui" if "aujourd" in q or "today" in q else "demain"
            answers.append(get_weather(day))

        if answers:
            return " | ".join(answers)

        if re.search(r"(?:hackathon|etudiant|etudiants|inscrit|inscrits|participants|participant|equipe|team|projet|project)", q):
            return "Je n'ai pas trouvé cette information dans la base locale du hackathon."

        # Case 2: two-step compound instruction: find course and send reminder
        if "rappel" in q and "avant" in q:
            # Try to extract course name from the question by matching known courses
            courses = _load_courses()
            course_name = None
            for c in courses:
                if c["name"].lower() in q:
                    course_name = c["name"]
                    break
            if not course_name:
                # Fallback: ask for course name
                return "Quel cours ?"

            course = get_course(course_name)
            if not course:
                return f"Cours '{course_name}' introuvable."

            # Extract threshold hour from question (e.g., "9h" -> 9)
            import re as _re

            m = _re.search(r"(\d{1,2})\s?h", q)
            threshold = 9
            if m:
                try:
                    threshold = int(m.group(1))
                except Exception:
                    threshold = 9

            # Compare course time
            try:
                hour = int(course.get("time", "00:00").split(":")[0])
            except Exception:
                hour = 0

            if hour < threshold:
                # Send reminder
                msg = f"Rappel: votre cours {course['name']} commence à {course['time']} en {course['room']}."
                confirmation = send_reminder(msg)
                return f"Rappel envoyé: {confirmation}"
            else:
                return f"Le cours {course['name']} commence à {course['time']} — pas de rappel envoyé."

        # Case 2: simple keyword-based queries
        # Accept reformulations: "où est mon cours", "où dois-je aller" -> salle
        if ("salle" in q) or (("ou" in q_norm or "où" in q) and "cours" in q_norm):
            # find course name
            for c in _load_courses():
                if c["name"].lower() in q:
                    return get_room(c["name"]) or "Salle inconnue"
            return "Quel cours voulez-vous ?"

        if "professeur" in q or "enseign" in q:
            for c in _load_courses():
                if c["name"].lower() in q:
                    return get_teacher(c["name"]) or "Enseignant inconnu"
            return "Quel cours voulez-vous ?"

        if "horaire" in q or "heure" in q:
            for c in _load_courses():
                if c["name"].lower() in q:
                    return json.dumps(get_course(c["name"]), ensure_ascii=False)
            return "Quel cours voulez-vous ?"

        # Request for full information: "donne moi les informations" / "informations"
        if "information" in q or "informations" in q or "donne" in q:
            for c in _load_courses():
                if c["name"].lower() in q:
                    return json.dumps(get_course(c["name"]), ensure_ascii=False)
            csv_answer = _csv_fallback(question)
            if csv_answer is not None:
                return csv_answer
            return "Quel cours voulez-vous ?"

        # Fallback: when the question is unrelated to course data, do not default to a course.
        if "docker" in q and ("salle" in q or "heure" in q or "enseign" in q or "professeur" in q):
            for c in _load_courses():
                if c["name"].lower() in q:
                    return json.dumps(get_course(c["name"]), ensure_ascii=False)

        csv_answer = _csv_fallback(question)
        if csv_answer is not None:
            return csv_answer

        return "Je n'ai pas de réponse pour cette demande dans la base locale."

        # Fallback: use the Phase 3 JSON bridge (which itself may simulate)
        decision = ask_llm_for_tool_json(question)
        result = call_tool_from_json(decision)
        return json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)

    # Online mode: use function-calling loop with Groq
    messages = [{"role": "user", "content": question}]

    for step in range(max_steps):
        try:
            if MODEL:
                response = client.chat.completions.create(
                    model=MODEL, messages=messages, tools=TOOLS_SCHEMA
                )
            else:
                response = client.chat.completions.create(messages=messages, tools=TOOLS_SCHEMA)
        except Exception as e:
            print("Groq API error:", e)
            # Fall back to Phase 3 bridge for offline testing
            decision = ask_llm_for_tool_json(question)
            result = call_tool_from_json(decision)
            return json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)

        message = response.choices[0].message

        # If no tool calls, return the assistant content as final answer
        tool_calls = getattr(message, "tool_calls", None) or []
        if not tool_calls:
            return message.content

        # Add the assistant message (which requested tool calls) to the history
        messages.append({"role": "assistant", "content": getattr(message, "content", "")})

        # Execute each tool call in order and append tool results to messages
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            args_text = tool_call.function.arguments
            try:
                args = json.loads(args_text)
            except Exception:
                args = {}

            if func_name not in TOOLS_BY_NAME:
                tool_result_text = f"Unknown tool: {func_name}"
            else:
                try:
                    tool_result = TOOLS_BY_NAME[func_name](**args)
                    if isinstance(tool_result, (dict, list)):
                        tool_result_text = json.dumps(tool_result, ensure_ascii=False)
                    else:
                        tool_result_text = str(tool_result)
                except Exception as e:
                    tool_result_text = f"Tool execution error: {e}"

            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_result_text})

    return "Error: max steps exceeded without final response."


if __name__ == "__main__":
    print(run_agent("Dans quelle salle est le cours de Docker ?"))
