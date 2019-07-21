import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  URL = os.environ.get('UGAMUSIC_HOT100_URL')
  DOWNLOAD_COUNT = int(os.environ.get('UGAMUSIC_DOWNLOAD_COUNT'))
  DOWNLOAD_DIRECTORY = os.environ.get('UGAMUSIC_DOWNLOAD_DIRECTORY')
  DATABASE_FILE = os.environ.get('UGAMUSIC_DATABASE_FILE')
  TASKS_FILE = os.environ.get('UGAMUSIC_TASKS_FILE')
