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
                  model: str = 'gpt-4o-mini', **parameters):
    if image is not None:
        # Make images available to the model by passing the image URL
        # or by passing the base64 encoded image
        base64_image = base64.b64encode(image).decode('utf-8')
        input = [{ 'role': 'user',
                   'content': [{ 'type': 'input_text', 'text': prompt },
                               { 'type': 'input_image',
                                 'image_url': f'data:image/jpeg;base64,{base64_image}' },
                              ]
                 }]
    else:
        input = prompt
    response = client.responses.create(
            model = model,
            input = input,
            **parameters,
        )
    return response.output_text
