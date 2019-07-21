from tinydb import TinyDB, Query
from settings import Config

db = TinyDB(Config.DATABASE_FILE)

Songs = Query()