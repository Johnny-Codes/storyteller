import os
import json
import sqlite3
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from StoryDB import StoryDB

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


def generate_tts(story):
    """
    Generates a TTS response from the story using the OpenAI API.
    """
    story_json = json.loads(story)
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


# Testing Code
generated_story = generate_story(prompt)
tts_file_path = generate_tts(generated_story)
story_db = StoryDB()
story_db.create_stories_db()
story_db.add_story_to_db(generated_story, tts_file_path)
