import os
from dotenv import load_dotenv

# Load environment variables from a '.env' file
load_dotenv()

from flask import Flask, request, abort, jsonify

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
    PushMessageRequest,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

from chat_bot import chat_bot

# Load secrets from environment variables
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

app = Flask(__name__)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# The /echo endpoint is used to echo back users' chat messages on LINE platform
@app.route('/echo', methods=['GET', 'POST'])
def echo(request):
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

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info('Invalid signature. Please check your channel access token/channel secret.')
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

import threading

from openai import OpenAI

client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY")
    # Otherwise use: api_key="Your_API_Key"
    api_key=os.environ['OPENAI_API_KEY'],
)

def async_get_response(user_id, prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{ "role": "user", "content": prompt, }],
    )
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=response.choices[0].message.content)]
            )
        )

# The /chat endpoint is called by the fulfillment of my intents on Dialogflow
@app.route('/chat', methods=['POST'])
def chat(request):
    json = request.get_json()
    query_result = json['queryResult']
    action = query_result.get('action')
    if action == 'input.unknown':
        # Relay the query text to chatGPT and asynchronous push back the response
        user_id = json['originalDetectIntentRequest']['payload']['data']['source']['userId']
        prompt  = query_result['queryText']
        CT = threading.Thread(target=async_get_response, args=(user_id, prompt,))
        CT.start()
        return jsonify({ 'fulfillmentText': '...' })

    return jsonify({ 'fulfillmentText': chat_bot(json) })

if __name__ == '__main__':
    port = os.environ.get('SERVER_PORT')
    if port == None:
        port = 80
    else:
        port = int(port)
    app.run(host='0.0.0.0', port=port)
