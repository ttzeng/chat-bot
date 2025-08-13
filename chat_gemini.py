import os

# Import the Google GenAI SDK
from google import genai
from google.genai import types

# The legacy SDK implicitly handled the API client using a variety of adhoc methods.
# The new SDK now introduces a central Client object, which acts as a single entry point
# for various API services (e.g., models, chats, files, tunings).
# Since an API client is created before calling the API, it picks up the API key
# from the environment variable 'GOOGLE_API_KEY' or 'GEMINI_API_KEY', if no API key passed
# explicitly.
client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

def get_response (prompt: str, image: bytes = None,
                  model: str = 'gemini-2.0-flash-lite', **parameters):
    # Generate text from inputs.
    # It's a single instance for single-turn queries. For multi-turn queries,
    # this is repeated field containing conversation history and latest request.
    if image is not None:
        # Provide the image data as bytes or Base64 encoded strings
        blob = types.Part.from_bytes(data=image, mime_type="image/jpeg")
        prompt = [ prompt, blob ]
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
