import os
import requests
import random
from bs4 import BeautifulSoup

from huey_config import huey
from tasks import fetch_download_link, fetch_song
from database import db, Song
from settings import Config


if __name__ == '__main__':
    Song.create_table()
    print('Beginning Hot100 Ugamusic scan')
    # Get page
    response = requests.get(Config.URL)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    # Pull the hot100 table
    top_100_table = soup.find('table', {'id': 'table-chart'})

    # Pull all the rows from the table body
    chart_rows = top_100_table.find('tbody').find_all('tr')

    if not len(chart_rows) == 100:
        print('Failed to find Hot100 table')
        
    # Pull details from each row
    new_songs = []
    for chart_row in chart_rows[:Config.DOWNLOAD_COUNT]:
        title = chart_row.find(class_='titlemeta')
        artist = chart_row.find(class_='namemeta')
        link = chart_row.find(class_='play-song', href=True)
        
        # Search the database for page (page w/song is like an uid)
        page = Song.select().where(Song.page == link['href'])
        if not page:
            print('Found new song: {0} - {1}'.format(artist.text, title.text))
            new_songs.append({
                'artist': artist.text, 
                'title': title.text, 
                'page': link['href'], 
            })
    if new_songs:
        with db.atomic():
            query = Song.insert_many(new_songs)
            query.execute()

    # Trigger tasks to get the download links
    songs = Song.select().where(Song.download_link.is_null(True))
    if songs:
        print('Will fetch the download link for {0} new songs'.format(len(songs)))
    for i, item in enumerate(songs):
        # Add an increasing delay so we don't abuse the servers
        delay = (30 * i) + random.randint(0, ( 60 * ( i / 2 ) ))
        fetch_download_link.schedule((item.page,), delay=delay)

    # Trigger tasks to get the songs
    songs = Song.select().where((Song.download_link.is_null(False)) & (Song.download_at.is_null(True)))
    if songs:
        print('Will download {0} songs'.format(len(songs)))
    for i, item in enumerate(songs):
        # Add an increasing delay so we don't abuse the servers
        delay = (30 * i) + random.randint(0, ( 60 * ( i / 2 ) ))
        fetch_song.schedule((item.download_link,), delay=delay)
