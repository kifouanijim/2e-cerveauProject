# Documentation du projet : Agent Python pour les cours, le hackathon et la météo

## 1. Objectif du projet

Le but de ce projet était de concevoir un assistant intelligent capable de répondre à des questions variées dans un contexte pédagogique et événementiel. L’agent devait notamment :

- répondre aux questions sur les cours (nom, salle, enseignant, horaire),
- simuler l’envoi d’un rappel,
- interroger des données sur les participants à un hackathon,
- donner la météo à Paris pour un jour donné,
- être utilisable dans une interface web simple.

Le projet a été construit progressivement, en partant d’un système très simple basé sur des mots-clés, puis en ajoutant des données structurées, un pont JSON avec un modèle LLM, puis enfin une vraie boucle d’agent avec Groq et une interface utilisateur.

---

## 2. Contexte et fil rouge

Le projet s’appuie sur un scénario concret :

- un étudiant veut savoir où se déroule un cours,
- il veut savoir qui l’enseigne,
- il souhaite recevoir un rappel avant le début du cours,
- il veut aussi connaître des informations sur le hackathon et la météo.

Le projet démarre avec une base de données en JSON pour les cours, puis s’enrichit avec une base SQLite pour les participants du hackathon, puis avec une API météo externe.

---

## 3. Structure du dépôt

Le projet est organisé de la manière suivante :

- `tools.py` : fonctions de base de l’agent pour manipuler les données de cours,
- `router.py` : routeur manuel basé sur des mots-clés,
- `agent.py` : cœur logique de l’agent, avec le JSON bridge et l’intégration Groq,
- `db_tools.py` : accès aux données SQLite sur les participants du hackathon,
- `weather_tool.py` : récupération des prévisions météo via Open-Meteo,
- `data/courses.json` : données du programme de cours,
- `build_db.py` : construction de la base SQLite,
- `hackathon.db` : base de données utilisée par l’agent,
- `app.py` : interface web Flask,
- `requirements.txt` : dépendances Python du projet,
- `.env` / `.env.example` : configuration de Groq.

---

## 4. Phase 1 : les outils de base

La première étape consistait à créer les fonctions métier qui permettent à l’agent d’exécuter des actions concrètes.

### 4.1 Fichier `tools.py`

Ce fichier contient les fonctions suivantes :

- `get_course(course_name)`
  - permet de retrouver les informations d’un cours à partir de son nom,
  - compare les noms sans tenir compte de la casse,
  - renvoie le dictionnaire complet du cours si trouvé.

- `get_room(course_name)`
  - renvoie uniquement la salle du cours.

- `get_teacher(course_name)`
  - renvoie uniquement le professeur du cours.

- `send_reminder(message)`
  - simule l’envoi d’un rappel,
  - affiche le message et renvoie une confirmation.

Cette étape a posé les bases de l’architecture de l’agent : il suffit à un agent d’appeler une fonction existante, sans devoir inventer directement les réponses.

### 4.2 Données de cours

Les cours sont stockés dans `data/courses.json`. Ce fichier contient des informations comme :

- nom du cours,
- professeur,
- salle,
- horaire,
- éventuellement d’autres informations d’usage.

Le chargement de ce fichier est fait via une fonction interne qui lit le JSON et retourne une liste de cours exploitable.

---

## 5. Phase 2 : le routeur manuel

Une fois les outils créés, le projet a évolué vers un système de décision plus simple : un routeur codé à la main.

### 5.1 Fichier `router.py`

Le routeur `route(question)` examine la question et décide quelle fonction appeler selon des mots-clés. Par exemple :

- si la question contient “salle”, il appelle `get_room`,
- si “professeur” ou “enseignant” est présent, il appelle `get_teacher`,
- si “horaire” ou “heure” est présent, il appelle `get_course`,
- si “rappel” est dans la question, il appelle `send_reminder`.

Ce système est volontairement simple et utile pour comprendre les limites d’une logique purement par mots-clés. Il montre rapidement qu’une question reformulée peut ne plus être reconnue correctement.

### 5.2 Limite du routeur manuel

Ce routeur est fragile parce qu’il repose entièrement sur des formes de phrases précises. Il ne comprend pas réellement le sens de la demande. C’est à ce moment que l’on a introduit l’intelligence artificielle.

---

## 6. Phase 3 : passage au modèle de langage via JSON

La deuxième grande étape a consisté à remplacer le routeur manuel par une logique plus intelligente : demander au modèle de langue de choisir l’outil à appeler.

### 6.1 Fichier `agent.py`

Dans `agent.py`, on définit :

- une instruction système qui dit au modèle : “choisis l’outil à utiliser”,
- un appel à l’API Groq,
- une réponse attendue sous forme de JSON,
- un parse JSON pour transformer la réponse en dictionnaire Python.

L’idée était la suivante :

- le modèle reçoit la question,
- il retourne un objet JSON du type :

```json
{
  "tool": "get_room",
  "arguments": {
    "course_name": "Docker"
  }
}
```

- Python lit cette structure et exécute la bonne fonction.

### 6.2 Pourquoi cette étape est importante

C’est la première vraie séparation entre :

- le raisonnement du modèle,
- l’exécution des actions réelles dans le code Python.

On a ainsi créé un comportement de type “agent” : le modèle ne fait pas directement la réponse, il choisit l’outil puis le code effectue l’action.

### 6.3 Fallback local

Un point important du projet a été la robustesse. Les modèles peuvent ne pas être disponibles ou peuvent produire une réponse invalide. C’est pourquoi un système de secours a été ajouté :

- si le modèle ne répond pas ou si la configuration manque,
- l’agent bascule vers une logique locale de détection de mots-clés.

Cela permet de conserver le projet testable même sans accès à l’API.

---

## 7. Phase 4 : intégration du hackathon via SQLite

Le programme s’est ensuite enrichi avec des données plus variées : les participants du hackathon.

### 7.1 Fichier `build_db.py`

Ce fichier construit une base SQLite à partir d’un fichier CSV. Il crée une table `participants` avec notamment :

- identifiant,
- nom de l’étudiant,
- équipe,
- nom du projet,
- technologies utilisées.

Cette étape a permis de passer d’un système basé uniquement sur des JSON statiques vers des données structurées et interrogables plus facilement.

### 7.2 Fichier `db_tools.py`

Ce fichier expose plusieurs fonctions utiles :

- `count_students()`
  - retourne le nombre total d’étudiants inscrits,

- `get_team_project(team)`
  - retourne les informations relatives à une équipe donnée,

- `find_student(name)`
  - permet de retrouver l’équipe et le projet d’un étudiant à partir de son nom.

Cette couche de données est essentielle pour répondre à des questions comme :

- “Combien d’étudiants participent ?”
- “Quel est le projet de l’équipe 1 ?”
- “À quelle équipe appartient Alice ?”

---

## 8. Ajout de la météo

Le projet ne se limite pas au contexte académique et au hackathon : il inclut également une intégration météo.

### 8.1 Fichier `weather_tool.py`

Le module `weather_tool.py` interroge l’API Open-Meteo pour récupérer les prévisions météo de Paris.

Les fonctions importantes sont :

- `_weather_description(code)` : transforme un code météorologique en texte lisible,
- `_resolve_day_index(day)` : détermine si l’utilisateur parle de aujourd’hui ou de demain,
- `get_weather(day)` : construit une phrase explicite avec le temps attendu et les températures.

Exemples de réponses :

- “À Paris, demain, le temps est couvert avec un maximum de 18°C et un minimum de 12°C.”

Cette fonctionnalité montre que l’agent est capable de combiner des sources externes, pas seulement des données locales.

---

## 9. Amélioration de la logique de décision

Le code d’`agent.py` a progressivement été enrichi pour détecter les différents types de questions :

- questions sur les cours,
- questions sur l’effectif du hackathon,
- questions sur les projets ou les équipes,
- questions sur la météo,
- questions sur les rappels,
- questions mixtes combinant plusieurs sujets.

Par exemple, l’agent peut maintenant répondre correctement à des requêtes du type :

- “Combien d’étudiants participent et quelle sera la météo demain ?”
- “Quel est le projet de l’équipe 1 et où se trouve le cours de Docker ?”

Pour cela, il a fallu mettre en place un mécanisme de traitement robuste des différents cas, en évitant de s’arrêter au premier résultat trouvé.

---

## 10. La boucle agentique avec Groq

La dernière étape importante a consisté à passer d’un simple “JSON bridge” à une vraie intégration d’agent fonctionnel avec Groq.

### 10.1 Protocole utilisé

Le modèle reçoit la question ainsi qu’une description des outils disponibles. Il décide ensuite quel outil appeler et avec quels arguments.

### 10.2 Outils exposés au modèle

L’agent expose notamment :

- `get_course`,
- `get_room`,
- `get_teacher`,
- `send_reminder`,
- `count_students`,
- `get_team_project`,
- `find_student`,
- `get_weather`.

Le modèle n’a donc pas besoin de “déduire” le résultat lui-même : il sélectionne le bon outil, et le code exécute la logique correspondante.

### 10.3 Pourquoi c’est une architecture agentique

Cette approche correspond à la définition d’un agent : un système capable de :

1. comprendre la question,
2. choisir une action adaptée,
3. appeler une fonction logicielle,
4. interpréter le résultat,
5. formuler une réponse claire pour l’utilisateur.

---

## 11. Interface utilisateur web

Pour rendre le projet plus agréable à utiliser, une interface web a été ajoutée.

### 11.1 Fichier `app.py`

Ce fichier construit une petite application Flask avec :

- un formulaire de saisie,
- une zone de texte pour poser la question,
- un bouton pour envoyer la requête,
- un espace d’affichage pour la réponse.

L’utilisateur peut maintenant poser des questions via le navigateur sans utiliser le terminal.

### 11.2 Exemple d’interaction

L’interface propose des exemples comme :

- “Combien d’étudiants participent ?”
- “Quel temps fera-t-il demain ?”
- “Quel est le projet de l’équipe 1 ?”
- “Où est le cours de Docker ?”

Cette étape marque l’aboutissement du projet : il est désormais utilisable comme un mini assistan t IA fonctionnel, interactif et accessible.

---

## 12. Résultat final atteint

À l’issue du projet, nous avons obtenu un agent capable de :

- répondre aux questions de cours,
- localiser les salles et professeurs,
- simuler l’envoi d’un rappel,
- gérer les données du hackathon,
- intégrer la météo parisienne,
- utiliser Groq pour la prise de décision intelligente,
- exécuter tout cela dans une interface web simple et fonctionnelle.

Le système fonctionne à la fois en mode logiciel local robuste et en mode agent LLM avec intégration de fonctions.

---

## 13. Points clés de l’apprentissage

Ce projet illustre plusieurs notions essentielles :

- séparation entre données, logique métier et intégration IA,
- importance des outils bien définis,
- rôle d’un routeur naïf pour comprendre les limites d’une approche trop simple,
- nécessité d’un mécanisme de fallback pour garantir la robustesse,
- intérêt d’intégrer des bases de données et des APIs externes,
- passage d’un système de terminal à une application plus conviviale via Flask.

---

## 14. Commandes utiles

Pour exécuter le projet localement :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Puis ouvrir :

```text
http://127.0.0.1:5000
```

---

## 15. Conclusion

Ce projet est un exemple complet de construction progressive d’un agent IA orienté outils. Il montre comment passer d’un simple script Python à un agent capable d’interagir avec des données, des APIs externes et une interface utilisateur.

Le résultat final va bien au-delà d’un simple chatbot : c’est un système d’assistance qui intègre des sources de données réelles, exécute des actions spécifiques et reste utilisable même en cas de défaillance de l’API du modèle.
