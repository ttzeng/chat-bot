import os
import base64

import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key = os.environ['ANTHROPIC_API_KEY'],
)

def get_response (prompt: str, image: bytes = None,
                  model: str = 'claude-sonnet-4-5-20250929',
                  **parameters):
    contents = []
    if image is not None:
        # Claude supports base64 source type for images with 'image/jpeg',
        # 'image/png', 'image/gif', 'image/webp' media types.
        # See below vision guide for more details.
        # https://docs.anthropic.com/en/docs/build-with-claude/vision
        contents.append({
            'type': 'image',
            'source': {
                'type': 'base64',
                'media_type': 'image/jpeg',
                'data': base64.b64encode(image).decode('utf-8'),
            },
        })
    contents.append({ 'type': 'text', 'text': prompt })
    response = client.messages.create(model = model,
                                      messages = [
                                          { 'role': 'user', 'content': contents }
                                      ],
                                      **parameters)
    return response.content[0].text
