import os

# Line Bot 設定
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '{bot_access_token}')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '{bot_webhook_id}')

# Imgur 設定
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID', '{imgur_client_id}')
IMGUR_CLIENT_SECRET = os.getenv('IMGUR_CLIENT_SECRET', '{imgur_client_secret}')
IMGUR_ACCESS_TOKEN = os.getenv('IMGUR_ACCESS_TOKEN', '{imgur_access_token}')
IMGUR_REFRESH_TOKEN = os.getenv('IMGUR_REFRESH_TOKEN', '{imgur_refresh_token}')

# 資料庫設定
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '{sql_server_ip}'),
    'port': 3306,
    'user': 'bnb_python',
    'passwd': '12345678',
    'db': 'bnb_wedding',
    'charset': 'utf8mb4'
}

# 圖片模板設定
TEMPLATE_IMAGES = {
    'portrait': [
        {'path': '/tmp/FeuDqBE.jpg', 'box': (90, 105, 652, 975)},
        {'path': '/tmp/jjkP1OO.jpg', 'box': (830, 114, 1393, 983)}
    ],
    'landscape': [
        {'path': '/tmp/ryUiTQb.jpg', 'box': (931, 435, 1802, 999)},
        {'path': '/tmp/cUiNFmq.jpg', 'box': (108, 517, 978, 1078)},
        {'path': '/tmp/yK2mEQK.jpg', 'box': (106, 1290, 970, 1847)}
    ],
    'download_list': [
        ("https://i.imgur.com/FeuDqBE.jpg", '/tmp/FeuDqBE.jpg'),
        ("https://i.imgur.com/jjkP1OO.jpg", '/tmp/jjkP1OO.jpg'),
        ("https://i.imgur.com/ryUiTQb.jpg", '/tmp/ryUiTQb.jpg'),
        ("https://i.imgur.com/cUiNFmq.jpg", '/tmp/cUiNFmq.jpg'),
        ("https://i.imgur.com/yK2mEQK.jpg", '/tmp/yK2mEQK.jpg')
    ]
} 