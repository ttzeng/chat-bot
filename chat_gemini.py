import os

# Import Generative Language API library
import google.ai.generativelanguage as glm

# Import the module of Python SDK for the Gemini API
import google.generativeai as genai

# Pass the API key to the SDK
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Select a model
model = genai.GenerativeModel('gemini-1.5-flash')

# Start a chat session for a multi-turn conversation
chat = model.start_chat(history=[])

def get_gemini_response (prompt: str, image: bytes = None):
    if image is not None:
        blob = glm.Blob(mime_type='image/jpeg', data=image)
        prompt = [ prompt, blob ]
    response = chat.send_message(prompt)
    return response.text
