import csv
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hackathon.db"
CSV_PATH = BASE_DIR / "data" / "hackathon_participants.csv"


def build_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS participants")
    cursor.execute(
        """
        CREATE TABLE participants (
            id INTEGER PRIMARY KEY,
            student_name TEXT NOT NULL,
            team INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            technologies TEXT NOT NULL
        )
        """
    )

    with CSV_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            cursor.execute(
                """
                INSERT INTO participants (id, student_name, team, project_name, technologies)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    int(row["id"]),
                    row["student_name"],
                    int(row["team"]),
                    row["project_name"],
                    row["technologies"],
                ),
            )

    conn.commit()
    conn.close()
    print(f"Base SQLite créée : {DB_PATH}")


if __name__ == "__main__":
    build_db()
