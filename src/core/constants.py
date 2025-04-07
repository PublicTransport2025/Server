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
