import os

# Import Generative Language API library
import google.ai.generativelanguage as glm

# Import the module of Python SDK for the Gemini API
import google.generativeai as genai

# Pass the API key to the SDK
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def get_response (prompt: str, image: bytes = None,
                  model: str = 'gemini-1.5-flash'):
    # Select the model
    model = genai.GenerativeModel(model)

    # Generate text from inputs.
    # It's a single instance for single-turn queries. For multi-turn queries,
    # this is repeated field containing conversation history and latest request.
    if image is not None:
        blob = glm.Blob(mime_type='image/jpeg', data=image)
        prompt = [ prompt, blob ]
    response = model.generate_content(prompt)
    return response.text
