import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def load_df():
    csv_candidates = list(ROOT.glob("*.csv")) + list(DATA_DIR.glob("*.csv"))

    if csv_candidates:
        return pd.read_csv(csv_candidates[0])

    json_path = DATA_DIR / "courses.json"
    with open(json_path, encoding="utf-8") as f:
        payload = json.load(f)
    return pd.json_normalize(payload)


def count_students():
    """Retourne le nombre total d'étudiants inscrits."""
    df = load_df()
    return int(df.shape[0])


def get_team_project(team):
    """Retourne le projet et les technologies pour une équipe donnée."""
    df = load_df()
    team_key = str(team).strip().lower()
    team_df = df[df["team"].astype(str).str.strip().str.lower() == team_key]

    if team_df.empty:
        return None

    row = team_df.iloc[0]
    return {
        "team": int(row["team"]),
        "project_name": row["project_name"],
        "technologies": [tech.strip() for tech in str(row["technologies"]).split(",")],
    }


if __name__ == "__main__":
    df = load_df()
    print(f"Data source: {DATA_DIR / 'hackathon_participants.csv'}")
    print("HEAD:")
    print(df.head())
    print("COLUMNS:")
    print(df.columns)
    print("SHAPE:")
    print(df.shape)
    print("TOTAL_STUDENTS:")
    print(count_students())
    print("TEAM_1_PROJECT:")
    print(get_team_project(1))
