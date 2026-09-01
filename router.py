"""
Phase 2 — Un routeur "naif", sans aucune intelligence artificielle.

Il choisit une fonction a appeler a partir de mots-cles presents dans la
question. C'est volontairement fragile : vous allez le tester avec
plusieurs formulations a la fin de cette phase pour observer ses limites.
"""
from tools import get_course, get_room, get_teacher, send_reminder


def route(question: str):
    """Renvoie la fonction outil a appeler selon des mots-cles simples.

    TODO : completez les conditions ci-dessous.
    """
    question = question.lower()
    if "salle" in question:
        return get_room
    if "professeur" in question or "enseign" in question:
        return get_teacher
    if "horaire" in question or "heure" in question:
        return get_course
    if "rappel" in question or "préviens" in question or "previens" in question:
        return send_reminder
    return None


if __name__ == "__main__":
    tests_simples = [
        "Dans quelle salle est Docker ?",
        "Qui enseigne Python ?",
        "A quelle heure est Docker ?",
    ]
    tests_reformules = [
        "Ou dois-je aller pour Docker ?",
        "Quel est le prof de Python ?",
        "Quand commence mon cours de Docker ?",
    ]

    print("--- Formulations attendues ---")
    for q in tests_simples:
        fn = route(q)
        print(f"{q!r} -> {fn.__name__ if fn else 'AUCUN OUTIL TROUVE'}")

    print("\n--- Defi : formulations reformulees ---")
    for q in tests_reformules:
        fn = route(q)
        print(f"{q!r} -> {fn.__name__ if fn else 'AUCUN OUTIL TROUVE'}")
