"""
Phase 1 — Les outils disponibles pour l'agent.

Un outil est une simple fonction Python : l'agent ne fait qu'appeler une
fonction qui existe déjà, il n'invente jamais lui-même le résultat.
"""
import json
from pathlib import Path

COURSES_PATH = Path(__file__).parent / "data" / "courses.json"


def _load_courses():
    with open(COURSES_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_course(course_name: str):
    """Exercice 1 — Renvoie toutes les informations d'un cours.

    TODO : parcourez la liste renvoyée par _load_courses() et renvoyez le
    dictionnaire dont la clé "name" correspond à course_name (comparaison
    insensible à la casse). Renvoyez None si aucun cours ne correspond.
    """
    raise NotImplementedError("À vous de jouer : Exercice 1")


def get_room(course_name: str):
    """Exercice 2 — Renvoie uniquement la salle d'un cours.

    TODO : réutilisez get_course() plutôt que de relire le fichier JSON.
    """
    raise NotImplementedError("À vous de jouer : Exercice 2")


def get_teacher(course_name: str):
    """Exercice 2 — Renvoie uniquement l'enseignant d'un cours.

    TODO : même logique que get_room().
    """
    raise NotImplementedError("À vous de jouer : Exercice 2")


def send_reminder(message: str):
    """Exercice 2 — Simule l'envoi d'un rappel (aucun vrai envoi).

    TODO : affichez le message avec print(), puis renvoyez une chaîne de
    confirmation, par exemple "Notification envoyée."
    """
    raise NotImplementedError("À vous de jouer : Exercice 2")


if __name__ == "__main__":
    # Exercice 3 : lancez `python tools.py` pour tester vos fonctions.
    print(get_course("Docker"))
    print(get_room("Docker"))
    print(get_teacher("Docker"))
    print(send_reminder("Test de notification"))
