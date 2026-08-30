# Atelier 3 — Développer son premier agent Python

Fil rouge : un agent capable de répondre à des questions sur les cours
(horaire, salle, enseignant) et d'envoyer un rappel.

## Installation (à faire en Phase 0)

```bash
python -m venv .venv
source .venv/bin/activate          # sous Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # puis collez votre clé Groq dans .env
```

Vérifiez que tout fonctionne :

```bash
python -c "import os, dotenv, groq; dotenv.load_dotenv(); print('OK' if os.environ.get('GROQ_API_KEY') else 'Clé manquante')"
```

## Organisation des fichiers

```
agent-python/
├── main.py          point d'entrée : lance une conversation avec l'agent
├── tools.py          les outils de l'agent (Phase 1)
├── router.py         le routeur codé à la main (Phase 2)
├── agent.py           le pont LLM -> JSON (Phase 3) puis la boucle agentique (Phase 4)
├── data/courses.json  le jeu de données du fil rouge
├── requirements.txt
└── .env.example
```

Chaque fichier contient des `TODO` à compléter dans l'ordre des phases. Testez
un fichier directement avec `python tools.py`, `python router.py` ou
`python agent.py` : chacun contient un petit bloc de test à la fin.

## Si vous êtes bloqués

Ce dépôt contient une branche `solutions` avec un commit par phase, chacun
marqué d'un tag :

```bash
git tag                     # liste les points de passage disponibles
git show v1-outils:tools.py # affiche la solution de la Phase 1 sans y toucher
```

Demandez au formateur avant de checkout une solution complète : l'objectif
est de rester bloqué juste assez longtemps pour comprendre le problème, pas
de sauter l'exercice.

## Utiliser Ollama à la place de Groq (optionnel)

Si vous préférez travailler en local plutôt que via l'API Groq (par exemple
en cas de coupure réseau), Ollama expose une API compatible : remplacez
l'initialisation du client dans `agent.py` par un client `OpenAI` pointant
vers `http://localhost:11434/v1`, et utilisez un modèle comme `qwen2.5`. La
sortie JSON d'un modèle local est moins fiable que celle de Groq : gardez
Groq comme option par défaut pendant l'atelier.
