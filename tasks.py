from os.path import join
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from huey_config import huey
from database import db, Song
from settings import Config


@huey.task(retries=3, retry_delay=300)
def fetch_download_link(page):
    '''Find the download link on the song page.'''
    # Get the song's webpage
    response = requests.get(page)
    # Parse the webpage
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the download link on the webpage
    link = soup.find('a', class_='song-download', href=True).get('href')
    # Add the download link to the database
    with db.atomic():
        query = Song.update(download_link=link).where(Song.page == page)
        query.execute()

@huey.task(retries=3, retry_delay=300)
def fetch_song(link):
    '''Download the song.'''
    # Fetch the song from the database that has this link
    song = Song.get(Song.download_link == link)
    # Get the file from the web
    response = requests.get(link)
    # Open a file on the computer and write the song to the file
    filename = '{0} - {1}.mp3'.format(song.artist, song.title)
    with open(join(Config.DOWNLOAD_DIRECTORY, filename), 'wb') as f:
        f.write(response.content)
    # Update the database so the song is not downloaded twice
    with db.atomic():
        query = Song.update(download_at=datetime.utcnow().timestamp()).where(Song.download_link == link)
        query.execute()
