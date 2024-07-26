import os
import base64

import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key = os.environ['ANTHROPIC_API_KEY'],
)

def get_response (prompt: str, image: bytes = None,
                  model: str = 'claude-3-5-sonnet-20240620',
                  max_tokens = 1024, temperature = 0.8):
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
                                      max_tokens = max_tokens,
                                      temperature = temperature,
                                      messages = [
                                          { 'role': 'user', 'content': contents }
                                      ])
    return response.content[0].text
