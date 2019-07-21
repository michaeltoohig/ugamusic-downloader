import requests
from bs4 import BeautifulSoup
from datetime import datetime

from huey_config import huey
from database import db, Songs
from settings import Config


@huey.task(retries=3, retry_delay=300)
def fetch_download_link(page):
    '''Find the download link on the song page.'''
    response = requests.get(page)
    soup = BeautifulSoup(response.text, 'html.parser')
    link = soup.find('a', class_='song-download', href=True).get('href')
    db.update({'download_link': link, 'download_at': False}, Songs.page == page)


@huey.task(retries=3, retry_delay=300)
def fetch_song(link):
    '''Download the song.'''
    song = db.search(Songs.download_link == link)
    if not song:
        pass
    song = song[0]
    response = requests.get(link)
    with open(f'{Config.DOWNLOAD_DIRECTORY}/{song.get("artist")} - {song.get("title")}.mp3', 'wb') as f:
        f.write(response.content)
    db.update({'download_at': datetime.utcnow().timestamp()}, Songs.download_link == link)
