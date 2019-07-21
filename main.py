import os
import requests
from bs4 import BeautifulSoup

from huey_config import huey
from tasks import fetch_download_link, fetch_song
from database import db, table, Songs
from tinyrecord import transaction
from settings import Config


if __name__ == '__main__':
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
        page = db.search(Songs.page == link['href'])
        if not page:
            print(f'Found new song: {artist.text} - {title.text}')
            new_songs.append({
                'artist': artist.text, 
                'title': title.text, 
                'page': link['href'], 
                'download_link': False,
            })
    if new_songs:
        with transaction(table) as tr:
            tr.insert_multiple(new_songs)

    # Trigger tasks to get the download links
    songs = db.search(Songs.download_link == False)
    if songs:
        print(f'Will fetch the download link for {len(songs)} new songs')
    for item in songs:
        fetch_download_link(item.get('page'))

    # Trigger tasks to get the songs
    songs = db.search((Songs.download_link.exists()) & (Songs.download_at == False))
    if songs:
        print(f'Will download {len(songs)} songs')
    for item in songs:
        fetch_song(item.get('download_link'))
