import os
from types import SimpleNamespace

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

s = SimpleNamespace()
try:
    # Load secrets from private module
    import secrets as sf
    s.LINE_CHANNEL_ACCESS_TOKEN = sf.LINE_CHANNEL_ACCESS_TOKEN
    s.LINE_CHANNEL_SECRET = sf.LINE_CHANNEL_SECRET
except ImportError:
    # Load secrets from environment variables
    s.LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    s.LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

app = Flask(__name__)
line_bot_api = LineBotApi(s.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(s.LINE_CHANNEL_SECRET)

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
