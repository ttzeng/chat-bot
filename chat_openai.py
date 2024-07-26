import os
import base64

from openai import OpenAI

client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY")
    # Otherwise use: api_key="Your_API_Key"
    api_key=os.environ['OPENAI_API_KEY'],
    # Optional specify which organization and project is used for an API request
    # organization='org-Bl1FC8TRewe26bsouN1DXCTD',
    # project='$PROJECT_ID',
)

def get_response (prompt: str, image: bytes = None,
                  model: str = 'gpt-4o', temperature = 0.8):
    if image is not None:
        # Make images available to the model by passing the image URL
        # or by passing the base64 encoded image
        base64_image = base64.b64encode(image).decode('utf-8')
        prompt = [ { 'type': 'text', 'text': prompt },
                   { 'type': 'image_url',
                     'image_url': { 'url': f'data:image/jpeg;base64,{base64_image}' }
                   }
                 ]
    response = client.chat.completions.create(
            model = model,
            messages = [ { "role":"user", "content": prompt } ],
            temperature = temperature,
        )
    return response.choices[0].message.content
