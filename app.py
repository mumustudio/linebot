from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import powerfulchatbot
import requests
import time


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('')
# Channel Secret
handler = WebhookHandler('')

# coding=UTF-8

def add_userid(userid):
    data = {'id': userid}
    print('新增id資料', data)
    r = requests.post('http://mumu.tw/mumu/php/Sara/AddId.php', data=data)
    print(r.text)


def find_coomand(userid):
    print('開始搜尋指令')
    data = {'id': userid}
    r = requests.post('http://mumu.tw/mumu/php/Sara/FindCommand.php', data=data)
    commands = r.text.split()
    for x in range(len(commands)):
        print('指令索引:'+str(x))
        print(commands[x])
    return commands


def reset_command(userid):
    print('清空指令')
    data = {'id': userid}
    requests.post('http://mumu.tw/mumu/php/Sara/ReSetCommand.php', data=data)


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
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
@handler.add(MessageEvent, message=LocationMessage)
@handler.add(MessageEvent, message=StickerMessage)
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    user_id = event.source.user_id
    add_userid(user_id)
    user_message_type=event.message.type
    #使用者傳送了 地理位置類型
    if user_message_type == 'location':
        user_MySql = find_coomand(user_id)
        reset_command(user_id)
        user_message = event.message
        powerful_reply = powerfulchatbot.get_MySql_command(user_MySql,user_message)
        print(powerful_reply)
        reply_type = powerful_reply.split(';')[0]
        reply_message = powerful_reply.split(';')[1]
    # 使用者傳送了一般文字訊息
    elif user_message_type == 'text':
        user_message = str(event.message.text)
        powerful_reply = powerfulchatbot.get_reply(user_message,user_id=user_id)
        print(type(powerful_reply))
        print(powerful_reply)
        reply_type = powerful_reply.split(';')[0]
        reply_message = powerful_reply.split(';')[1]
    # 使用者傳送了貼圖訊息
    elif user_message_type == 'sticker':
        print('收到貼圖訊息')
        requests.post('http://mumu.tw/jarvis/confirmcommand.php')
        time.sleep(1)
        requests.post('http://mumu.tw/jarvis/playmusic.php')
        line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id='1',sticker_id=410))
    elif user_message_type == 'image':
        print('收到圖片訊息')
        image_id=event.message.id
        imagecontent=line_bot_api.get_message_content(image_id)
        with open("./tempjpg", 'wb') as fd:
            for chunk in imagecontent.iter_content():
                fd.write(chunk)
        powerful_reply=powerfulchatbot.image_recognition("./tempjpg")
        reply_type = powerful_reply.split(';')[0]
        reply_message = powerful_reply.split(';')[1]
    print(powerful_reply)
    # 回覆給使用者的格式
    if reply_type == 'text':
        print('文字回覆格式 開始回覆')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
    elif reply_type == 'img':
        powerful_reply=powerful_reply.split(';')[1]
        original_img_url=powerful_reply.split(' ')[0]
        print('大圖: '+original_img_url)
        preview_img_url=powerful_reply.split(' ')[1]
        print('小圖: '+preview_img_url)
        message = ImageSendMessage(
            original_content_url=original_img_url,
            preview_image_url=preview_img_url
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif reply_type == 'buttontemplate':
        powerful_reply = powerful_reply.split(';')[1]
        messageobject = powerful_reply.split(' ')
        _imageurl = messageobject[0]
        _title = messageobject[1]
        _text = messageobject[2]
        _label = messageobject[3]
        print('imageurl:'+_imageurl)
        print('title: '+_title)
        print('text: '+_text)
        print('label: '+_label)
        if len(messageobject)==5:
            _actionurl=messageobject[4]
            print('acitonurl: '+_actionurl)
        else:
            _actionurl=' '
        # 圖片文字回覆格式:圖片網址 標題 內文 按鈕 [目標網站(選填)]
        buttons_template = TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                title=_title,
                text=_text,
                thumbnail_image_url=_imageurl,
                actions=[
                    MessageTemplateAction(
                        label=_label,
                        text=_actionurl
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)




import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
