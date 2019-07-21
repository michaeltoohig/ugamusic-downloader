from huey import SqliteHuey
from settings import Config

huey = SqliteHuey(filename=Config.TASKS_FILE)