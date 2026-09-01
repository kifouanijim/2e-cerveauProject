from flask import Flask, render_template_string, request
from agent import run_agent

app = Flask(__name__)

HTML_PAGE = """
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Agent Hackathon</title>
    <style>
      :root {
        --bg: #f3f7ff;
        --panel: #ffffff;
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --muted: #64748b;
        --border: #dfeaf7;
        --answer-bg: #edf5ff;
        --answer-border: #bfdbfe;
        --shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Segoe UI", Arial, sans-serif;
        background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
        color: #0f172a;
      }

      .container {
        max-width: 920px;
        margin: 48px auto;
        padding: 28px;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 24px;
        box-shadow: var(--shadow);
      }

      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 24px;
        flex-wrap: wrap;
      }

      .badge {
        display: inline-block;
        padding: 8px 12px;
        border-radius: 999px;
        background: #dbeafe;
        color: var(--primary-dark);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
      }

      h1 {
        margin: 0;
        font-size: clamp(2rem, 2vw, 2.5rem);
      }

      form {
        display: grid;
        gap: 14px;
      }

      textarea {
        width: 100%;
        min-height: 120px;
        resize: vertical;
        padding: 16px 18px;
        border-radius: 16px;
        border: 1px solid var(--border);
        background: #f8fbff;
        color: #0f172a;
        font: inherit;
        font-size: 1rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
      }

      textarea:focus {
        outline: none;
        border-color: rgba(37, 99, 235, 0.7);
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
      }

      .actions {
        display: flex;
        justify-content: flex-end;
      }

      button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 12px;
        font: inherit;
        font-weight: 700;
        cursor: pointer;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 12px 24px rgba(37, 99, 235, 0.2);
      }

      button:hover {
        transform: translateY(-1px);
      }

      .examples {
        margin-top: 18px;
        color: var(--muted);
        font-size: 0.95rem;
      }

      .examples-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
      }

      .examples span {
        display: inline-block;
        background: #eef2ff;
        color: #334155;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid #dfe7ff;
      }

      .answer {
        margin-top: 26px;
        background: var(--answer-bg);
        border: 1px solid var(--answer-border);
        border-left: 5px solid var(--primary);
        padding: 18px 20px;
        border-radius: 14px;
        white-space: pre-wrap;
        line-height: 1.6;
      }

      .answer-label {
        display: inline-block;
        margin-bottom: 8px;
        font-weight: 700;
        color: var(--primary-dark);
      }

      @media (max-width: 640px) {
        .container {
          margin: 20px 12px;
          padding: 20px 16px;
        }

        .header {
          align-items: flex-start;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <div>
          <span class="badge">Assistant IA</span>
          <h1>Agent Hackathon</h1>
        </div>
      </div>

      <form method="post">
        <textarea name="question" placeholder="Posez votre question ici...">{{ current_question }}</textarea>
        <div class="actions">
          <button type="submit">Envoyer</button>
        </div>
      </form>

      <div class="examples">
        <div>Exemples de questions :</div>
        <div class="examples-list">
          <span>Combien d'étudiants participent ?</span>
          <span>Quel temps fera-t-il demain ?</span>
          <span>Quel est le projet de l'équipe 1 ?</span>
          <span>Où est le cours de Docker ?</span>
        </div>
      </div>

      {% if answer %}
      <div class="answer">
        <div class="answer-label">Réponse</div>
        {{ answer }}
      </div>
      {% endif %}
    </div>
  </body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    current_question = ""
    if request.method == "POST":
        current_question = request.form.get("question", "").strip()
        if current_question:
            try:
                answer = run_agent(current_question)
            except Exception as e:
                answer = f"Erreur lors du traitement : {str(e)}"
    return render_template_string(HTML_PAGE, answer=answer, current_question=current_question)


if __name__ == "__main__":
    print("🚀 Démarrage du serveur Flask...")
    print("📍 Adresse : http://127.0.0.1:5000")
    print("🔒 Le serveur ne répond qu'aux questions basées sur les données locales du projet.")
    print("⛔ Aucune réponse générale ou externe n'est fournie.")
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)
