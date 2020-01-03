from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

if __name__ == "__main__":
    app.run()

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


# 處理訊息
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # 被動 Reply Message 使用 replyToken 這個 key 裡面的資訊來回復訊息
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    data = air()
    # message = TextSendMessage(text="請輸入'空氣'來得知訊息"+event.message.text)

    k = 0
    try:
        if event.message.text == "今天":
            message = TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    thumbnail_image_url='https://upload.cc/i1/2020/01/02/psRVCD.jpg',
                    title='功能選單',
                    text='Please select',
                    actions=[
                        # PostbackTemplateAction是含有值的訊息回覆
                        PostbackTemplateAction(
                            label='空氣品質查詢',
                            text='空氣品質查詢',
                            # data='action=buy&itemid=1'
                            data='postback1'
                        ),

                        # ),
                        # URITemplateAction是網址的使用
                        URITemplateAction(
                            label='前往中央氣象局',
                            uri='https://www.cwb.gov.tw/V8/C/W/W50_index.html'
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
            TextSendMessage(text=message)

        if event.message.text == "空氣":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入位置"))

        if event.message.text == "空氣品質查詢":
            message = TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://upload.cc/i1/2020/01/03/17Pspz.jpg',
                            title='高雄市',
                            text='description1',
                            actions=[
                                MessageTemplateAction(
                                    label='高雄(左營)',
                                    text='高雄(左營)',
                                ),
                                MessageTemplateAction(
                                    label='高雄(楠梓)',
                                    text='高雄(楠梓)',
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://upload.cc/i1/2020/01/03/ZskDji.jpg',
                            title='台北市',
                            text='description2',
                            actions=[
                                MessageTemplateAction(
                                    label='萬華',
                                    text='萬華',
                                ),
                                MessageTemplateAction(
                                    label='大同',
                                    text='大同',
                                )

                            ]
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)

        else:
            for i in data:
                value = [i["County"], i["SiteName"], i["Status"]]
                # if event.message.text == value[0]:
                if event.message.text == i["SiteName"]:
                    k = k + 1
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="您所查詢的空氣品質" + value[2]))
            if k == 0:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請重新輸入"))
    except:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="發生錯誤"))
