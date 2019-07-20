import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tinydb import TinyDB, Query
from tinydb.operations import set
from huey import SqliteHuey, crontab

db = TinyDB('stores/ugamusic.db')
huey = SqliteHuey('./tasks.db')

# Create query object for our db
Songs = Query()


#@huey.task(retries=3, retry_delay=300)
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
    print('fetching song')
    response = requests.get(link)
    print(response)
    with open(f'downloads/{song.get("artist")} - {song.get("title")}.mp3', 'wb') as f:
        f.write(response.content)
    db.update({'download_at': datetime.utcnow().timestamp()}, Songs.download_link == link)


# Get page
#response = requests.get('https://ugamusic.biz/hot100')
#with open('pages/ugamusic-hot100.html', 'w') as f:
#    f.write(response.text)

with open('pages/ugamusic-hot100.html', 'r') as f:
    page = f.read()

# Create a BeautifulSoup object
soup = BeautifulSoup(page, 'html.parser')

# Pull the hot100 table
top_100_table = soup.find('table', {'id': 'table-chart'})

# Pull all the rows from the table body
chart_rows = top_100_table.find('tbody').find_all('tr')

# Pull details from each row
for chart_row in chart_rows[:3]:
    title = chart_row.find(class_='titlemeta')
    artist = chart_row.find(class_='namemeta')
    link = chart_row.find(class_='play-song', href=True)
    
    # Search the database for page (page w/song is like an uid)
    page = db.search(Songs.page == link['href'])
    if not page:
        db.insert({
            'artist': artist.text, 
            'title': title.text, 
            'page': link['href'], 
            'download_link': False,
        })



# Trigger tasks to get the download links
for item in db.search(Songs.download_link == False):
    #print(item)
    fetch_download_link(item.get('page'))

# Trigger tasks to get the songs
for item in db.search((Songs.download_link.exists()) & (Songs.download_at == False)):
    print(item)
    fetch_song(item.get('download_link'))

print('done')