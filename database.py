from peewee import *
from settings import Config

db = SqliteDatabase(Config.DATABASE_FILE)

class Song(Model):
    artist = CharField()
    title = CharField()
    page = CharField(unique=True)
    download_link = CharField(null=True)
    download_at = DateField(null=True)

    class Meta:
        database = db
