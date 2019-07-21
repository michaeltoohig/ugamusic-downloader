from tinydb import TinyDB, Query
from settings import Config

db = TinyDB(Config.DATABASE_FILE)
table = db.table()

# Create a query object for the songs in our database
Songs = Query()