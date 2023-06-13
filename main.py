import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from chat_bot import chat_bot

# Load secrets from environment variables
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route('/echo', methods=['GET', 'POST'])
def _echo():
    return echo(request)

def echo(request):
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        message)

@app.route('/chat', methods=['POST'])
def _chat():
    return chat(request)

def chat(request):
    return jsonify({ 'fulfillmentText': chat_bot(request.get_json()) })

if __name__ == '__main__':
    port = os.environ.get('SERVER_PORT')
    if port == None:
        port = 80
    else:
        port = int(port)
    app.run(host='0.0.0.0', port=port)
