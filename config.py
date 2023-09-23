import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_OWNER = os.getenv('BOT_OWNER')
GROUP_ID = os.getenv('GROUP_ID')