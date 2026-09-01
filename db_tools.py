import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "hackathon.db"


def _connect():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database manquante : {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def count_students():
    """Retourne le nombre total d'étudiants inscrits."""
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM participants").fetchone()
    return int(row["total"])


def get_team_project(team):
    """Retourne le projet et les technologies pour une équipe donnée."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT team, project_name, technologies FROM participants WHERE team = ? LIMIT 1",
            (int(team),),
        ).fetchone()

    if row is None:
        return None

    return {
        "team": int(row["team"]),
        "project_name": row["project_name"],
        "technologies": [tech.strip() for tech in str(row["technologies"]).split(",")],
    }


def find_student(name):
    """Retourne l'équipe et le projet d'un étudiant à partir de son nom."""
    query_name = str(name).strip()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT student_name, team, project_name
            FROM participants
            WHERE LOWER(student_name) = LOWER(?)
            LIMIT 1
            """,
            (query_name,),
        ).fetchone()

    if row is None:
        return None

    return {
        "student_name": row["student_name"],
        "team": int(row["team"]),
        "project_name": row["project_name"],
    }


if __name__ == "__main__":
    print("TOTAL_STUDENTS:")
    print(count_students())
    print("TEAM_1_PROJECT:")
    print(get_team_project(1))
    print("FIND_STUDENT:")
    print(find_student("Alice Martin"))
