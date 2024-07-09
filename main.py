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

import requests
from chat_gemini import get_gemini_response
from chat_openai import get_openai_response
from chat_claude import get_claude_response
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

        # Consult Redis API endpoint on model setting
        queries = { 'model': '' }
        r = requests.get(os.environ.get('API_REDIS'), params=queries)
        model = r.json().get('model')
        if model == 'gemini':
            response = get_gemini_response(event.message.text, image)
        elif model == 'openai':
            response = get_openai_response(event.message.text, image)
        elif model == 'claude':
            response = get_claude_response(event.message.text, image)
        else:
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
