# Ugamusic Downloader

> Does not work as intended. TinyDB can not handle multiple processes. Will replace with database with sqlite.

This is a simple downloader for (Ugamusic)[www.ugamusic.biz]. It will find and download new songs from the `Hot100` list. But it keeps a simple database so that it won't download any songs more than once and uses a task manager to add automatic retries to failed downloads.

Run this script once a day or once a week to get the newest hot 100 songs.

It is built using these projects:
  - (TinyDB)[https://github.com/msiemens/tinydb] Database
  - (Huey)[https://github.com/coleifer/huey] Task Manager
  - (BeautifulSoup)[https://www.crummy.com/software/BeautifulSoup/bs4/doc/] for web scraping
  - (Requests)[https://2.python-requests.org/en/master/] for fetching URLs

I filled the project with many comments and hopefully kept things very clear and concise for new programmers to learn from and contribute.

Please don't abuse Ugamusic servers by scanning too often. Once a day will get you all the new hot releases.

## Installation

Clone this repo on to your machine.

```
git clone https://github.com/michaeltoohig/ugamusic-downloader
```

I recommend using a virtual environment then installing the requirements. 
Learn about virtual environments (here)[https://realpython.com/python-virtual-environments-a-primer/].

```
cd ugamusic-downloader
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

First copy the example environments file then edit your environments file.
In the environment file I define where files will be saved and even how many files it downloads. I only want the top 20 somethng songs and not all 100, you can modify yours if you want more or less.

```
cp .env.example .env
```

Then you will need to start two processes. One for fetching the 100 songs from ugamusic and a second process to actually download the file.

Start the task manager.

```
huey_consumer.py -w 3 main.huey
```

Then run the `main` file periodically via `cron` or on your own to kickstart the downloads. You may have to run it twice since there are two tasks, one for fetching the download link and a second task for downloading the file.

```
python main.py
```

## Roadmap

In the future I may add other music blogs or music release websites and I would like to reconfigure this project to work more like `youtubedl` with multiple extensions, one for each website.

Short-term this project could be wrapped up in a `dockerfile`.

Another option is to add functionality to download all the songs of a particular artist or other page from the website.

The project lacks proper logging or error reporting so if this is running long-term it would be hard to know that it failed due to Ugamusic updating the website unless you were paying attention to the downloads. This would be necessary if I go ahead with the first idea.

It would be nice if there was an automatic trigger that fired when a new `download_link` is added to start downloading the song. The project is simple and runs on a cron job so I currently wait for the next run of the script to start the downloads but this is not ideal.