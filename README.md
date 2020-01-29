# Scraper for everynoise.com

## Installation
- Install Python distribution via Anaconda
- Install scrapy (toolkit for webscraping)
`pip install scrapy` 

## Running
- Run everynoise.py file (weekly)
`python everynoise.py`

- Run everynoise_worldbrowser.py file (hourly)
`python everynoise_worldbrowser.py`

## Content of web scraper

### Weekly releases to Spotify, by country
![Screenshot](/doc/everynoise_newrelease_by_genre.png)

### Spotify World browser; featured playlists by category (hour if available), and country
![Screenshot](/doc/everynoise_worldbrowser.png)

**Documentation of JSON file structure**

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
