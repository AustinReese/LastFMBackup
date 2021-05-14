import pylast
import sqlite3
from csv import DictWriter
from json import dumps
from os import environ

API_KEY = environ["LASTFM_API_KEY"]
API_SECRET = environ["LASTFM_SHARED_SECRET"]
USER = environ["USER"]
FILENAME = f"./{USER}_scrobbles.csv"


def saveTracks():
    # Set up LastFM API
    pylast_network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
    )
    user = pylast_network.get_user(USER)

    print(f"Fetching all tracks from {USER}")
    played_tracks = user.get_recent_tracks(limit=None)
    formatted_tracks = []

    print(f"Scraped {len(played_tracks)} scrobbles from user {USER}")
    print("Formatting data...")

    count = 0
    for played_track in played_tracks:
        count += 1
        # format title to handle alternative titles by slicing off text followed by - character
        title = played_track.track.title
        bad_strings = [" remaster", " version", " mix", " mono", " live", " alternate", " demo", " including", " edit"]
        if '-' in title and any(bad_str in title.lower() for bad_str in bad_strings):
            title = "-".join(title.split('-')[:-1]).strip()

        artist = played_track.track.artist.name
        format_dict = {"title": title,
                       "artist": artist,
                       "album": played_track.album,
                       "playback_date": played_track.playback_date,
                       "duration": played_track.track.get_duration(),
                       "musicbrainz_id": played_track.track.get_mbid(),
                       "listener_count": played_track.track.get_listener_count(),
                       "playcount": played_track.track.get_playcount(),
                       "timestamp": played_track.timestamp}

        # Fetch all tags
        top_tags = played_track.track.get_top_tags(limit=50)

        album = played_track.track.get_album()
        if len(top_tags) == 0 and album != None:
            try:
                top_tags = album.get_top_tags(limit=50)
            except pylast.WSError as e:
                print(e)

        if len(top_tags) == 0:
            print(f"No tags found for {title} by {artist}")

        tag_dict = {}
        for tag in top_tags:
            # Store only tags with strong weight and ignore tags that are the artists name
            if int(tag.weight) >= 10 and artist.lower() != tag.item.name.lower():
                tag_dict[tag.item.name] = tag.weight

        # Convert tag_dict to JSON and add to master list
        format_dict["tags"] = dumps(tag_dict)
        formatted_tracks.append(format_dict)

        if count % 100 == 0:
            print(f"{count}/{len(played_tracks)}")

    print(f"{count}/{len(played_tracks)}")

    conn = sqlite3.connect("main.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS lastfm_tracks")
    curs.execute('''CREATE TABLE IF NOT EXISTS lastfm_tracks(title TEXT NOT NULL, artist TEXT NOT NULL, album TEXT NOT NULL,
                 playback_date TEXT NOT NULL, timestamp BIGINT NOT NULL, duration INT, musicbrainz_id INT, listener_count INT,
                 playcount INT, tags TEXT)''')

    for track_dict in formatted_tracks:
        to_insert = (track_dict["title"], track_dict["artist"], track_dict["album"], track_dict["playback_date"],
                     track_dict["timestamp"], track_dict["duration"], track_dict["musicbrainz_id"],
                     track_dict["listener_count"], track_dict["playcount"], track_dict["tags"])
        sql_insert = '''
            INSERT INTO lastfm_tracks(title, artist, album, playback_date, timestamp, duration, musicbrainz_id, listener_count, playcount, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
        curs.execute(sql_insert, to_insert)
    conn.commit()
    conn.close()

    print(f"Writing to {FILENAME}")
    csv_keys = formatted_tracks[0].keys()
    with open(FILENAME, 'w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, csv_keys)
        writer.writeheader()
        writer.writerows(formatted_tracks)


def main():
    saveTracks()
    # fetchDetails()


if __name__ == "__main__":
    main()

