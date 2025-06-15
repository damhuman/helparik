import configparser
import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('POSTGRES_URL')

BOT_TOKEN = os.getenv('TOKEN')

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

L1_RPC_URL = os.getenv('L1_RPC_URL')
ENCRYPTION_PASSWORD = os.getenv('ENCRYPTION_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
INTMAX_BACKEND_URL = os.getenv('INTMAX_URL')

ua_config = configparser.ConfigParser()
ua_config.read('bot/locales/ua/strings.ini')
