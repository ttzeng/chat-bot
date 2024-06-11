import os

# Import the module of Python SDK for the Gemini API
import google.generativeai as genai

# Pass the API key to the SDK
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Select a model
model = genai.GenerativeModel('gemini-pro')

# Start a chat session for a multi-turn conversation
chat = model.start_chat(history=[])

def get_gemini_response (prompt):
    response = chat.send_message(prompt)
    return response.text
