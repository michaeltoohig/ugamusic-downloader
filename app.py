import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tinydb import TinyDB, Query
from huey import SqliteHuey

db = TinyDB('stores/ugamusic.db')
huey = SqliteHuey('tasks.db')

if False:
    page = requests.get('https://ugamusic.biz/hot100')
    page = page.text
    with open('top100.html', 'w') as f:
        f.write(page)
else:
    f = open('top100.html', 'r')
    page = f.read()
    f.close()


# Create a BeautifulSoup object
soup = BeautifulSoup(page, 'html.parser')

# Pull all text from the BodyText div
top_100_table = soup.find('table', {'id': 'table-chart'})

# Pull text from all instances of <a> tag within BodyText div
chart_rows = top_100_table.find('tbody').find_all('tr')

# Create query object for our db
Songs = Query()

# Pull details from each row
for chart_row in chart_rows:
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
            'downlaod_link': None,
            'download_at': None,
        })
