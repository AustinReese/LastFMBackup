import sqlite3
import grequests
import requests
from json import loads
from Track import Track
from urllib.parse import quote
from time import sleep

class LastFmApiDriver:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://ws.audioscrobbler.com/2.0/?"


    def save_recent_tracks(self, user: str) -> list:
        self.recreate_table(user)
        page_count = 1
        total_pages = 1
        page_limit = 200
        tracks = []
        previously_parsed_info_urls = {}
        print("Downloading recently played tracks...")
        while total_pages >= page_count:
            recent_tracks_response = requests.get(f"{self.base_url}method=user.getrecenttracks&user={user}&api_key={self.api_key}&format=json&limit={page_limit}&page={page_count}")
            recent_tracks_response_dict = loads(recent_tracks_response.text)
            while "error" in recent_tracks_response_dict:
                print(f"{recent_tracks_response_dict['message']} Pausing execution for 3 seconds and retrying.")
                sleep(3)
                recent_tracks_response = requests.get(
                    f"{self.base_url}method=user.getrecenttracks&user={user}&api_key={self.api_key}&format=json&limit={page_limit}&page={page_count}")
                recent_tracks_response_dict = loads(recent_tracks_response.text)

            recent_tracks_dict = recent_tracks_response_dict["recenttracks"]

            total_pages = int(recent_tracks_dict["@attr"]["totalPages"])
            recent_track_data = recent_tracks_dict["track"]
            info_urls = [f"{self.base_url}method=track.getInfo&api_key={self.api_key}&track={quote(i['name'])}&artist={quote(i['artist']['#text'])}&format=json" for i in recent_track_data]
            info_results = grequests.map(grequests.get(u) for u in info_urls if u not in previously_parsed_info_urls)
            #info_results = info_results + [previously_parsed_info_urls[u] for u in info_urls if u in previously_parsed_info_urls]
            #assert len(info_urls) == len(info_results)
            assert len(info_urls) == len(recent_track_data)
            for i in range(len(info_urls)):
                if info_urls[i] not in previously_parsed_info_urls:
                    previously_parsed_info_urls[info_urls[i]] = info_results[i]
                else:
                    info_results.insert(i, previously_parsed_info_urls[info_urls[i]])
                track_info_dict = loads(info_results[i].text)

                if "track" not in track_info_dict:
                    track_info_dict["track"] = {}
                    track_info_dict["track"]["toptags"]= {}
                    track_info_dict["track"]["toptags"]["tag"] = []
                    track_info_dict["track"]["duration"] = 0
                    track_info_dict["track"]["listeners"] = 0
                    track_info_dict["track"]["playcount"] = 0
                tags = []
                for tag in track_info_dict["track"]["toptags"]["tag"]:
                    tags.append(tag["name"])
                track = Track(recent_track_data[i]["name"],
                            recent_track_data[i]["mbid"],
                            recent_track_data[i]["artist"]["#text"],
                            recent_track_data[i]["artist"]["mbid"],
                            recent_track_data[i]["album"]["#text"],
                            recent_track_data[i]["album"]["mbid"],
                            track_info_dict["track"]["duration"],
                            track_info_dict["track"]["listeners"],
                            track_info_dict["track"]["playcount"],
                            str(tags),
                            recent_track_data[i]["date"]["uts"],
                            recent_track_data[i]["date"]["#text"])
                track.save(user)
            print(f"{round((page_limit * page_count)/(page_limit * total_pages) * 100, 2)}%")
            page_count += 1
        print("Download complete")
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
