import requests
from bs4 import BeautifulSoup
from datetime import datetime

from huey_config import huey
from database import db, Songs
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
    db.update({'download_link': link, 'download_at': False}, Songs.page == page)


@huey.task(retries=3, retry_delay=300)
def fetch_song(link):
    '''Download the song.'''
    # Fetch the song from the database that has this link
    song = db.search(Songs.download_link == link)
    # There should only be one item in the `song` list; grab the first
    song = song[0]
    # Get the file from the web
    response = requests.get(link)
    # Open a file on the computer and write the song to the file
    with open(f'{Config.DOWNLOAD_DIRECTORY}/{song.get("artist")} - {song.get("title")}.mp3', 'wb') as f:
        f.write(response.content)
    # Update the database so the song is not downloaded twice
    db.update({'download_at': datetime.utcnow().timestamp()}, Songs.download_link == link)
