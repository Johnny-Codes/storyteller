from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_story(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a wise grandma who is trying to tell a story to their grandchild based on what they want to hear. Return a JSON Object with a story title and the story",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=1.0,
    )

    return response.choices[0].message.content


prompt = "Tell me a story about a bear lost in the woods."

print(generate_story(prompt))
