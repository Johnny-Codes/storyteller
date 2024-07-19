import sqlite3
import json
from contextlib import contextmanager


class StoryDB:
    def __init__(self, db_path="stories.db"):
        self.db_path = db_path

    @contextmanager
    def db_cursor(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        try:
            yield cur
        finally:
            con.commit()
            con.close()

    def create_stories_db(self):
        with self.db_cursor() as cur:
            cur.execute(
                """
                    CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY, title TEXT, story TEXT, tts TEXT)
                """
            )

    def add_story_to_db(self, story, tts_file_path):
        story = json.loads(story)
        with self.db_cursor() as cur:
            cur.execute(
                """
                    INSERT INTO stories (title, story, tts) VALUES (?, ?, ?)
                """,
                (story["title"], story["story"], str(tts_file_path)),
            )

    def get_story_from_db(self, title):
        with self.db_cursor() as cur:
            res = cur.execute(
                """
                    SELECT tts FROM stories WHERE title LIKE ? COLLATE NOCASE;
                """,
                (f"{title}%",),
            )
            return res.fetchall()

    def delete_story_from_db(self, title):
        with self.db_cursor() as cur:
            cur.execute(
                """
                    DELETE FROM stories WHERE title LIKE ?;
                """,
                (f"{title}",),
            )
