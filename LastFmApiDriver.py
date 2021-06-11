import requests
import sqlite3
from json import loads
from Track import Track
from urllib.parse import quote

class LastFmApiDriver:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://ws.audioscrobbler.com/2.0/?"


    def save_recent_tracks(self, user: str) -> list:
        self.recreate_table(user)
        page_count = 1
        total_pages = 1
        tracks = []
        saved_tracks = {}
        while total_pages >= page_count:
            recent_tracks_response = requests.get(f"{self.base_url}method=user.getrecenttracks&user={user}&api_key={self.api_key}&format=json&limit=200&page={page_count}")
            recent_tracks_dict = loads(recent_tracks_response.text)["recenttracks"]
            total_pages = int(recent_tracks_dict["@attr"]["totalPages"])
            raw_tracks = recent_tracks_dict["track"]
            
            for i in raw_tracks:
                if (f"{i['name']}_{i['artist']}") in saved_tracks:
                    saved_tracks[f"{i['name']}_{i['artist']}"].save(user)
                    continue
                track_info_response = requests.get(f"{self.base_url}method=track.getInfo&api_key={self.api_key}&track={quote(i['name'])}&artist={quote(i['artist']['#text'])}&format=json")
                track_info_dict = loads(track_info_response.text)
                tags = []
                for tag in track_info_dict["track"]["toptags"]["tag"]:
                    tags.append(tag["name"])
                track = Track(i["name"],
                            i["mbid"],
                            i["artist"]["#text"],
                            i["artist"]["mbid"],
                            i["album"]["#text"],
                            i["album"]["mbid"],
                            track_info_dict["track"]["duration"],
                            track_info_dict["track"]["listeners"],
                            track_info_dict["track"]["playcount"],
                            str(tags),
                            i["date"]["uts"],
                            i["date"]["#text"])
                saved_tracks[f"{i['name']}_{i['artist']}"] = track
                track.save(user)
            page_count += 1
        return tracks

    def recreate_table(self, user: str):
        conn = sqlite3.connect("main.db")
        curs = conn.cursor()
        curs.execute(f"DROP TABLE IF EXISTS lastfm_tracks_{user}")
        curs.execute(f"CREATE TABLE IF NOT EXISTS lastfm_tracks_{user}(\
                     title TEXT NOT NULL,\
                     musicbrainz_id TEXT NULL,\
                     artist TEXT NOT NULL,\
                     artist_musicbrainz_id TEXT NULL,\
                     album TEXT NOT NULL,\
                     album_musicbrainz_id TEXT NULL,\
                     duration INT NULL,\
                     listeners INT NULL,\
                     playcount INT NULL,\
                     tags TEXT NULL,\
                     played_timestamp TEXT NOT NULL,\
                     played_date TEXT)")
        conn.commit()
        conn.close()