import json
import os
from dotenv import load_dotenv

# Load environment variables from a '.env' file
load_dotenv()

from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    ImageMessageContent,
    TextMessageContent
)

# Load secrets from environment variables
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

app = Flask(__name__)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# The /callback endpoint is used to receive LINE message events through the webhook
@app.route('/callback', methods=['POST'])
def callback(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info('Invalid signature. Please check your channel access token/channel secret.')
        abort(400)
    return 'OK'

import re
import requests
import chat_gemini
import chat_openai
import chat_claude
from object_storage import (
    cloud_storage_upload_object,
    cloud_storage_download_object,
)

bucket_name = 'bucket-line-bot-storage'

def object_name(id: str) -> str:
    return '{}.jpg'.format(id)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # Download the quoted image if this message quotes a past message
        quoted_message_id = event.message.quoted_message_id
        image = (cloud_storage_download_object(bucket_name, object_name(quoted_message_id))
                 if quoted_message_id is not None else None)

        # Look for a word following a '@' and name the group as 'attn',
        # put the remaining string in the group 'msg'
        m = re.search(r'(?P<attn>(?<=^@)\w+)(\s*)(?P<msg>.*)', event.message.text)
        provider = m.group('attn') if m else None
        prompt   = m.group('msg')  if provider else event.message.text

        # Select the chat module according to the name of attention if provided and valid,
        # otherwise, consult Redis API endpoint on model configuration
        modules = {
            'gemini': chat_gemini,
            'openai': chat_openai,
            'claude': chat_claude,
        }
        model = None
        chat_bot = modules.get(provider) if provider else None
        if chat_bot is None:
            queries = { 'model': '' }
            r = requests.get(os.environ.get('API_REDIS'), params=queries)
            conf = json.loads(r.json().get('model'))
            provider = conf.get('provider')
            model    = conf.get('model')
            chat_bot = modules.get(provider)

        try:
            get_response = getattr(chat_bot, 'get_response')
            if model is None:
                # Use the default model of the chat module
                response = get_response(prompt=prompt, image=image)
            else:
                response = get_response(model=model, prompt=prompt, image=image)
        except AttributeError:
            print(f'Error: invalid provider \'{provider}\'')
            response = event.message.text

        # Generate text response from the message inputs
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response)]
            )
        )

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    with ApiClient(configuration) as api_client:
        api_blob = MessagingApiBlob(api_client)
        message_id = event.message.id
        cloud_storage_upload_object(bucket_name, object_name(message_id),
                                    api_blob.get_message_content(message_id),
                                    'image/jpeg')

if __name__ == '__main__':
    port = os.environ.get('SERVER_PORT')
    if port == None:
        port = 80
    else:
        port = int(port)
    app.run(host='0.0.0.0', port=port)
