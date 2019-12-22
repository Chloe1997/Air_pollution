from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,StickerMessage,StickerSendMessage
)
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


app = Flask(__name__)

line_bot_api = LineBotApi('rIxk6stOI6lawIZHAP8D5JNzvH09Rc4XTddGEUZJ327Npj+Rddp1gRVXAdAo/nONSZtr+t95qu2iZJ/MHuKpJy/qtT9ddV3SMVwaYVkz5onz76vrTIE3yy1YLxZ1meS5K9lmrbpBgDXZNr5aXbFsLAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d6bf376091a8e30931e9545e8b2908bc')


@app.route("/")
def home():
    return 'home OK'

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def air():
    r = requests.get("https://opendata.epa.gov.tw/ws/Data/AQI/?$format=json", verify=False)
    list_of_dicts = r.json()
    return list_of_dicts

#處理訊息
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    data = air()
    k=0
    try:
        if event.message.text == "空氣":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入位置"))
        else:
            for i in data:
                value = [i["County"], i["SiteName"], i["Status"]]
                if event.message.text == i["SiteName"] :
                    k = k+1
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="您所查詢的空氣品質"+value[2]))
            if k == 0:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請重新輸入"))
    except :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="發生錯誤"))


if __name__ == "__main__":
    app.run()

