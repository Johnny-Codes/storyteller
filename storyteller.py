import os
import json
import sqlite3
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
prompt = "a bear that befriends a ladybug"


def generate_story(prompt):
    """
    Generates a story from the prompt using the OpenAI API.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a sweet grandma who is trying to tell a story to their grandchild based on what they want to hear. Return a JSON Object with a title and the story",
            },
            {"role": "user", "content": "tell me a story about " + prompt},
        ],
        max_tokens=1000,
        temperature=1.3,
    )

    return response.choices[0].message.content


def generate_tts(story, story_json):
    """
    Generates a TTS response from the story using the OpenAI API.
    """
    file_name = story_json["title"]
    speech_file_path = Path(__file__).parent / f"{file_name}.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=story,
    )
    with open(speech_file_path, "wb") as f:
        for chunk in response.iter_bytes():
            f.write(chunk)
    return speech_file_path


"""
sqlite database for stories
"""


def create_stories_db():
    """
    Creates the stories.db sqlite3 database.
    Stories table with columns of title (text), story (text), tts (text - path to file)
    tts is converted from a Windows file path to a string.
    Have to look at this code on an RPI since it's linux based.
    """
    con = sqlite3.connect("stories.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY, title TEXT, story TEXT, tts TEXT)"
    )
    con.commit()
    con.close()


def add_story_to_db(story, tts_file_path):
    """
    adds the story title, text, and filepath (converted to string) of the mp3 to the database.
    """
    con = sqlite3.connect("stories.db")
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO stories (title, story, tts) VALUES (?, ?, ?)
        """,
        (story["title"], story["story"], str(tts_file_path)),
    )
    con.commit()
    con.close()


def get_story_from_db(title):
    con = sqlite3.connect("stories.db")
    cur = con.cursor()
    res = cur.execute(
        """
    SELECT tts FROM stories WHERE title LIKE ? COLLATE NOCASE;
    """,
        (f"{title}%",),
    )
    story = res.fetchall()
    return story


# generated_story = generate_story(prompt)
# generated_story_json = json.loads(generated_story)
# generate_tts_response = generate_tts(generated_story, generated_story_json)
if not os.path.isfile("stories.db"):
    create_stories_db()
# add_story_to_db(generated_story_json, generate_tts_response)
print(get_story_from_db("the bear"))
