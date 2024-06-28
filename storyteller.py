from openai import OpenAI
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
prompt = "a mermaid who saves her father the king of the sea"


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
                "content": "You are a wise grandma who is trying to tell a story to their grandchild based on what they want to hear. Return a JSON Object with a title and the story",
            },
            {"role": "user", "content": "tell me a story about " + prompt},
        ],
        max_tokens=1000,
        temperature=1.0,
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


generated_story = generate_story(prompt)
generated_story_json = json.loads(generated_story)
generate_tts_response = generate_tts(generated_story, generated_story_json)


"""
sqlite database for stories
"""
