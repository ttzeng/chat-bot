import os

from openai import OpenAI

client = OpenAI(
  # Defaults to os.environ.get("OPENAI_API_KEY")
  # Otherwise use: api_key="Your_API_Key"
  api_key=os.environ['OPENAI_API_KEY'],
)

def get_openai_response (prompt, model = 'gpt-3.5-turbo', temperature = 0.8):
    response = client.chat.completions.create(
            model = model,
            messages = [ { "role":"user", "content": prompt } ],
            temperature = temperature,
        )
    return response.choices[0].message.content
