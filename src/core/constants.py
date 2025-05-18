import os

from dotenv import load_dotenv

load_dotenv()

LOCALHOST_IP = os.getenv('LOCALHOST')
PORT = int(os.getenv('PORT'))

VERSION = os.getenv('VERSION')
API_KEY = os.getenv('API_KEY')

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

WEB_CLIENT_ID = os.getenv('WEB_CLIENT_ID')
WEB_CLIENT_SECRET = os.getenv('WEB_CLIENT_SECRET')
WEB_REDIRECT_URI = os.getenv('WEB_REDIRECT_URI')

MOBILE_CLIENT_ID = os.getenv('MOBILE_CLIENT_ID')
MOBILE_CLIENT_SECRET = os.getenv('MOBILE_CLIENT_SECRET')
MOBILE_REDIRECT_URI = os.getenv('MOBILE_REDIRECT_URI')

MAP_KEY = os.getenv('MAP_KEY')

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-default-secret')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 90))