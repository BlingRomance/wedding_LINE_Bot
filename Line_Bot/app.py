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
from config import (
    CHANNEL_ACCESS_TOKEN,
    CHANNEL_SECRET,
    IMGUR_CLIENT_ID,
    IMGUR_CLIENT_SECRET,
    IMGUR_ACCESS_TOKEN,
    IMGUR_REFRESH_TOKEN,
    DB_CONFIG,
    TEMPLATE_IMAGES
)

app = Flask(__name__)

# Line Bot 初始化
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Imgur 客戶端初始化
imgur_client = ImgurClient(
    IMGUR_CLIENT_ID,
    IMGUR_CLIENT_SECRET,
    IMGUR_ACCESS_TOKEN,
    IMGUR_REFRESH_TOKEN
)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'tmp')
os.makedirs(static_tmp_path, exist_ok=True)

def get_db_connection():
    """建立資料庫連接"""
    return MySQLdb.connect(**DB_CONFIG)

def save_blessing_to_db(name, content):
    """儲存祝福訊息到資料庫"""
    try:
        with get_db_connection() as db:
            cursor = db.cursor()
            sql = "INSERT INTO wedding_blessing(wedding_blessing_name, wedding_blessing_content) VALUES(%s, %s)"
            cursor.execute(sql, (name, content))
            db.commit()
        return True
    except Exception as e:
        print(f"資料庫錯誤: {e}")
        return False

def get_seat_number(name):
    """查詢座位號碼"""
    try:
        with get_db_connection() as db:
            cursor = db.cursor()
            sql = "SELECT wedding_sit_no FROM wedding_sit WHERE wedding_sit_name = %s"
            cursor.execute(sql, (name,))
            return cursor.fetchone()
    except Exception as e:
        print(f"資料庫錯誤: {e}")
        return None

def process_image(image_path):
    """處理上傳的圖片"""
    cover_img = Image.open(image_path)
    is_portrait = cover_img.size[1] > cover_img.size[0]
    
    # 選擇適當的模板
    if is_portrait:
        template = random.choice(TEMPLATE_IMAGES['portrait'])
    else:
        template = random.choice(TEMPLATE_IMAGES['landscape'])
    
    base_img = Image.open(template['path'])
    region = cover_img.resize((
        template['box'][2] - template['box'][0],
        template['box'][3] - template['box'][1]
    ))
    base_img.paste(region, template['box'])
    base_img.save(image_path)
    return image_path

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
    if isinstance(event.message, TextMessage):
        handle_text_message(event)
    elif isinstance(event.message, ImageMessage):
        handle_image_message(event)

def handle_text_message(event):
    text = event.message.text.lower()
    
    if text == "甜蜜時刻":
        send_random_wedding_photo(event)
    elif text == "美好當下":
        send_upload_instruction(event)
    elif text == "祝福新人":
        send_blessing_instruction(event)
    elif "ya" in text:
        handle_blessing(event)
    elif text == "愛的問答":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "https://docs.google.com/")
        )
    elif text == "專屬位子":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "請輸入關鍵字(T)與全名\n\n輸入範例：T簡紹庭")
        )
    elif str(text).find("T") != -1 or str(text).find("t") != -1:
        try:
            sit_1, sit_2 = str(text).split('T', 1)
        except Exception as e:
            pass

        try:
            sit_1, sit_2 = str(text).split('t', 1)
        except Exception as e:
            pass

        try:
            db = MySQLdb.connect(host = DB_CONFIG['host'], port = 3306, user = 'bnb_python', passwd = '12345678', db = 'bnb_wedding', charset = 'utf8mb4')
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
    elif text == "創意設計":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "創意構想\n軟體設計：新郎 Bling\n\n圖片協助：新娘 Beth\n\n視窗協助：煥博 Chris\n\n合成協助：瑜芳 Fish\n\n贊助廠商：\nhttps://shopee.tw/emilychien0514")
        )
    elif text == "限時活動":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "https://admin-official.line.me/")
        )

def handle_image_message(event):
    ext = 'jpg'
    message_content = line_bot_api.get_message_content(event.message.id)
    # Rename and save uploaded picture
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
    # Uploaded picture -> straight/horizontal
    # Randomly use picture templates
    # Uploaded is straight
    if cover_img.size[1] > cover_img.size[0]:
        index = random.randint(0, 1)
        if index == 0:
            base_img = Image.open('/tmp/FeuDqBE.jpg')
            box = (90, 105, 652, 975)

        if index == 1:
            base_img = Image.open('/tmp/jjkP1OO.jpg')
            box = (830, 114, 1393, 983)
    # Uploaded is horizontal
    else:
        index = random.randint(0, 2)

        if index == 0:
            base_img = Image.open('/tmp/ryUiTQb.jpg')
            box = (931, 435, 1802, 999)

        if index == 1:
            base_img = Image.open('/tmp/cUiNFmq.jpg')
            box = (108, 517, 978, 1078)

        if index == 2:
            base_img = Image.open('/tmp/yK2mEQK.jpg')
            box = (106, 1290, 970, 1847)

    # Use PIL to resize picture and photomontage
    region = region.resize((box[2] - box[0], box[3] - box[1]))
    base_img.paste(region, box)
    base_img.save(path)

    # Upload picture to imgur
    try:
        client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET, IMGUR_ACCESS_TOKEN, IMGUR_REFRESH_TOKEN)
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

    # Reply picture to user
    wedding_cover = client.get_album_images('n7W1A')
    for send_cover in wedding_cover:
        if send_cover.name == dist_name:
            message = ImageSendMessage(
                original_content_url = send_cover.link,
                preview_image_url = send_cover.link
            )
        line_bot_api.reply_message(event.reply_token, message)

    # Insert picture link from imgur to database
    try:
        db = MySQLdb.connect(host = DB_CONFIG['host'], port = 3306, user = 'bnb_python', passwd = '12345678', db = 'bnb_wedding', charset = 'utf8mb4')
        cursor = db.cursor()
        sql = """INSERT INTO wedding_image(wedding_image_link) VALUES('""" + send_cover.link + """')"""
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

    db.close()

if __name__ == "__main__":
    # 下載模板圖片
    for image_url, local_path in TEMPLATE_IMAGES['download_list']:
        urlretrieve(image_url, local_path)
    
    # 獲取婚禮相簿照片
    wedding_photos = imgur_client.get_album_images('Yjwsl')
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
