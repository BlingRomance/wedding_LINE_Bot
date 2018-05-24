from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from imgurpython import ImgurClient

from urllib.request import urlretrieve
from PIL import Image

import requests
import os
import random
import tempfile
import MySQLdb
import re
import time

app = Flask(__name__)

channel_access_token = '{bot_access_token}'
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler('{bot_webhook_id}')

client_id = '{imgur_client_id}'
client_secret = '{imgur_client_secret}'
access_token = '{imgur_access_token}'
refresh_token = '{imgur_refresh_token}'

static_tmp_path = os.path.join(os.path.dirname(__file__), '/tmp')

@app.route("/callback", methods = ['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text = True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message = (TextMessage, ImageMessage))
def handle_message(event):
    # receive key word -> send message or do something
    if isinstance(event.message, TextMessage):
        if event.message.text == "甜蜜時刻":
            index = random.randint(0, len(wedding_photos) - 1)
            url = wedding_photos[index].link

            message = ImageSendMessage(
                original_content_url = url,
                preview_image_url = url
            )
            line_bot_api.reply_message(event.reply_token, message)

        elif event.message.text == "美好當下":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "快上傳您的自拍照或與親友的合照，您的照片會顯示在大螢幕上喔！")
            )

        elif event.message.text == "祝福新人":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "請輸入關鍵字(YA)與祝福話，您的祝福會顯示在大螢幕上喔！\n\n輸入範例：YA新婚快樂")
            )

        elif str(event.message.text).find("ya") != -1 or str(event.message.text).find("YA") != -1 or str(event.message.text).find("Ya") != -1 or str(event.message.text).find("yA") != -1:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "謝謝您的祝福，大螢幕即將顯示您的祝福！！")
            )

            try:
                blessing_1, blessing_2 = str(event.message.text).split('ya', 1)
            except Exception as e:
                pass

            try:
                blessing_1, blessing_2 = str(event.message.text).split('YA', 1)
            except Exception as e:
                pass

            try:
                blessing_1, blessing_2 = str(event.message.text).split('Ya', 1)
            except Exception as e:
                pass

            try:
                blessing_1, blessing_2 = str(event.message.text).split('yA', 1)
            except Exception as e:
                pass
            # line user name
            profile = line_bot_api.get_profile(event.source.user_id)
            display_name = profile.display_name
            # 清除使用者名稱的特殊符號
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    "]+", flags = re.UNICODE)
            display_name = emoji_pattern.sub(r'', display_name)

            try:
                db = MySQLdb.connect(host = '{sql_server_ip}', port = 3306, user = 'bnb_python', passwd = '12345678', db = 'bnb_wedding', charset = 'utf8mb4')
                cursor = db.cursor()
                sql = """INSERT INTO wedding_blessing(wedding_blessing_name, wedding_blessing_content) VALUES('""" + display_name + """', '""" +  blessing_2 + """')"""
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()

            db.close()

        elif event.message.text == "愛的問答":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "https://docs.google.com/")
            )

        elif event.message.text == "專屬位子":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "請輸入關鍵字(T)與全名\n\n輸入範例：T簡紹庭")
            )

        elif str(event.message.text).find("T") != -1 or str(event.message.text).find("t") != -1:
            try:
                sit_1, sit_2 = str(event.message.text).split('T', 1)
            except Exception as e:
                pass

            try:
                sit_1, sit_2 = str(event.message.text).split('t', 1)
            except Exception as e:
                pass

            try:
                db = MySQLdb.connect(host = '{sql_server_ip}', port = 3306, user = 'bnb_python', passwd = '12345678', db = 'bnb_wedding', charset = 'utf8mb4')
                cursor = db.cursor()
                sql = """SELECT wedding_sit_no FROM bnb_wedding.wedding_sit WHERE wedding_sit_name = '""" + sit_2 + """'"""
                cursor.execute(sql)
                tup = cursor.fetchone()

                if tup != None:
                    sit_no =  ','.join('%s' %id for id in tup)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text = sit_2 + " 您好，您的座位在第 " + sit_no + " 桌")
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text = "請洽詢接待人員，將有專人為您帶位")
                    )
            except:
                db.rollback()

            db.close()

        elif event.message.text == "創意設計":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "創意構想\n軟體設計：新郎 Bling\n\n圖片協助：新娘 Beth\n\n視窗協助：煥博 Chris\n\n合成協助：瑜芳 Fish\n\n贊助廠商：\nhttps://shopee.tw/emilychien0514")
            )
        '''
        elif event.message.text == "限時活動":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "https://admin-official.line.me/")
            )

        elif event.message.text == "問答名單":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "https://docs.google.com/")
            )
        '''
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
        message_content = line_bot_api.get_message_content(event.message.id)
        #將上傳的照片命名並儲存
        with tempfile.NamedTemporaryFile(dir = static_tmp_path, prefix = ext + '-', delete = False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name

        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)
        path = os.path.join('/tmp', dist_name)

        cover_img = Image.open(path)
        region = cover_img
        # 判斷使用者上傳的照片是直/橫
        # 隨機使用照片樣板
        # 上傳為直
        if cover_img.size[1] > cover_img.size[0]:
            index = random.randint(0, 1)
            # 直1
            if index == 0:
                base_img = Image.open('/tmp/FeuDqBE.jpg')
                box = (90, 105, 652, 975)
            # 直2
            if index == 1:
                base_img = Image.open('/tmp/jjkP1OO.jpg')
                box = (830, 114, 1393, 983)
        # 上傳為橫
        else:
            index = random.randint(0, 2)
            # 橫1
            if index == 0:
                base_img = Image.open('/tmp/ryUiTQb.jpg')
                box = (931, 435, 1802, 999)
            # 橫2
            if index == 1:
                base_img = Image.open('/tmp/cUiNFmq.jpg')
                box = (108, 517, 978, 1078)
            # 橫3
            if index == 2:
                base_img = Image.open('/tmp/yK2mEQK.jpg')
                box = (106, 1290, 970, 1847)
        # 利用PIL調整上傳的照片大小並與照片樣板做合成
        region = region.resize((box[2] - box[0], box[3] - box[1]))
        base_img.paste(region, box)
        base_img.save(path)
        # 將合成完之照片上傳至imgur讓投影做使用
        try:
            client = ImgurClient(client_id, client_secret, access_token, refresh_token)
            config = {
                'album': 'n7W1A',
                'name': dist_name,
                'title': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'description': ''
            }
            
            client.upload_from_path(path, config = config, anon = False)
            os.remove(dist_path)
        except:
            pass
        # 將合成完之照片回傳給使用者
        wedding_cover = client.get_album_images('n7W1A')
        for send_cover in wedding_cover:
            if send_cover.name == dist_name:
                message = ImageSendMessage(
                    original_content_url = send_cover.link,
                    preview_image_url = send_cover.link
                )
            line_bot_api.reply_message(event.reply_token, message)
        # 將合成完之照片網址寫入資料庫讓投影做使用
        try:
            db = MySQLdb.connect(host = '{sql_server_ip}', port = 3306, user = 'bnb_python', passwd = '12345678', db = 'bnb_wedding', charset = 'utf8mb4')
            cursor = db.cursor()
            sql = """INSERT INTO wedding_image(wedding_image_link) VALUES('""" + send_cover.link + """')"""
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

        db.close()

if __name__ == "__main__":
    # 下載儲存照片樣板
    # 直1
    image_url = "https://i.imgur.com/FeuDqBE.jpg"
    urlretrieve(image_url, '/tmp/FeuDqBE.jpg')
    # 直2
    image_url = "https://i.imgur.com/jjkP1OO.jpg"
    urlretrieve(image_url, '/tmp/jjkP1OO.jpg')
    # 橫1
    image_url = "https://i.imgur.com/ryUiTQb.jpg"
    urlretrieve(image_url, '/tmp/ryUiTQb.jpg')
    # 橫2
    image_url = "https://i.imgur.com/cUiNFmq.jpg"
    urlretrieve(image_url, '/tmp/cUiNFmq.jpg')
    # 橫3
    image_url = "https://i.imgur.com/yK2mEQK.jpg"
    urlretrieve(image_url, '/tmp/yK2mEQK.jpg')

    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    wedding_photos = client.get_album_images('Yjwsl')

    app.run(host = '0.0.0.0', port = int(os.environ['PORT']))
    #app.run()