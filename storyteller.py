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
    response.stream_to_file(speech_file_path)
    return speech_file_path


generated_story = generate_story(prompt)
generated_story_json = json.loads(generated_story)
print(generated_story_json)
generate_tts_response = generate_tts(generated_story, generated_story_json)


"""
sqlite database for stories
"""


def create_stories_db():
    """
    Creates the stories.db sqlite3 database.
    Stories table with columns of title (text), story (text), tts (text - path to file)
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
    adds the story title, text, and filepath of the mp3 to the database.
    """
    print("add to story title", story["title"])
    print("add to story title", story["story"])
    print("add to story tts file path", tts_file_path)
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


create_stories_db()
add_story_to_db(generated_story_json, generate_tts_response)
