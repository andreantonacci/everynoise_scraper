# Scraper for everynoise.com

## Overview

This repository contains two webscrapers to collect data from everynoise.com. 

(1) **New releases**: A list of (weekly) album and single releases to Spotify, by country
![Screenshot](/doc/everynoise_newrelease_by_genre.png)

*The data is scraped from everynoise.com/new_releases_by_genre.cgi.*

(2) **Worldbrowser**: A list of "promoted"/"featured" playlists on Spotify, by playlist category, hour-of-the-day (if available), and country

![Screenshot](/doc/everynoise_worldbrowser.png)

*The data is collected from everynoise.com/worldbrowser.cgi.*

## Collecting the raw data

First, please install...
- Python distribution via Anaconda
- Scrapy (toolkit for webscraping)
  `pip install scrapy` 

Then, you can run the data collections:
- Run everynoise.py file (weekly)
`python everynoise.py`

- Run everynoise_worldbrowser.py file (hourly)
`python everynoise_worldbrowser.py`

## Documentation of output

The two webscrapers write the output of the data collections to JSON files.

(1) **New releases**

The data is written to new-line separated JSON files, named everynoise_newreleases_YYYYMMDD.json (whereas YYYYMMDD refers to the datestamp when the scraper was run.

*JSON file structure*

``` 
{
  "countryCode": "EC", # two-letter country code
  "trackId": "spotify:track:2rRhbOTbTwAUq45qdllfST", # Spotify track ID of track
  "artistId": "spotify:artist:07YUOmWljBTXwIseAUd9TW", # Spotify artist ID associated with track
  "rank": "EC rank: 10", # 
  "artistName": "Sebastián Yatra", # Artist name
  "albumId": "spotify:album:2B4n5Uy0rYJ1btdqtUsrw8", # Spotify album ID
  "albumName": "Un Año (En Vivo)", # Album name
  "scrapeUnix": 1570447279, # Unix time stamp when the data was scraped
  "scrapeDate": "20191007", # Datestamp when the data was scraped
  "everynoiseDate": "20191004" # Date when track/album was released to Spotify
}

``` 

(2) **Worldbrowser**

The data is written to new-line separated JSON files, named everynoise_worldbrowser_YYYYMMDD__HHMM.json (whereas YYYYMMDD refers to the datestamp, and HHMM to the hour-minute timestamp when the scraper was run.


*JSON file structure*

```
{
  "sectionName": "featured",
  "countryName": "Global",
  "countryCode": "3",
  "playlistIdArray": [
    "spotify:playlist:37i9dQZF1DX3rxVfibe1L0",
    "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
    "spotify:playlist:37i9dQZF1DX1s9knjP51Oa",
    "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd",
    "spotify:playlist:37i9dQZF1DX4pUKG1kS0Ac",
    "spotify:playlist:37i9dQZF1DWSXBu5naYCM9",
    "spotify:playlist:37i9dQZF1DWXRqgorJj26U",
    "spotify:playlist:37i9dQZF1DX7ZUug1ANKRP",
    "spotify:playlist:37i9dQZF1DWWQRwui0ExPn",
    "spotify:playlist:37i9dQZF1DWYmmr74INQlb",
    "spotify:playlist:37i9dQZF1DX2Nc3B70tvx0",
    "spotify:playlist:37i9dQZF1DWVViFqIfGGV7"
  ],
  "scrapeUnix": 1572350843,
  "scrapeDate": "20191029",
  "everyNoiseHour": "08:07am",
  "everyNoiseHourReference": "-23"
}
```

* SectionName: Playlist category, one of Featured, Top Lists, Pop, Hip-Hop, Mood, Decades, Country, Workout, Rock, Latin, Focus, Chill, Dance/Electronic, Tastemakers, R&B, Indie, Folk & Acoustic, Party, Wellness, Sleep, Classical, Jazz, Soul, Christian, Gaming, Romance, K-Pop, Anime, Pop culture, Arab, Desi, Afro, Comedy, Metal, Regional Mexican, Reggae, Blues, Punk, Funk, Student, Dinner, Black history is now, Spotify Singles, Commute, Kids & Family, Word, Yoga, Nature Sounds, Self love, Exercise, Meditation.
* CountryName: Country
* CountryCode: Country in numeric coding
* playlistIdArray: Spotify playlist IDs that were featured in a given category
* scrapeUnix: Unix timestamp of data retrieval (seconds passed since 1970-01-01, 00:00)
* scrapeDate: Date of data retrieval
* everyNoiseHour: Playlists from the *featured* category vary by hour of the day
* everyNoiseHourReference: Coding of everynoise hour category
