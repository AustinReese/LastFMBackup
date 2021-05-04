import pylast
from os import environ
from csv import DictWriter
import codecs

from idna import unicode

API_KEY = environ["LASTFM_API_KEY"]
API_SECRET = environ["LASTFM_SHARED_SECRET"]
#USER = environ["USER"]
USER = "slishslosh"
FILENAME = f"./{USER}_scrobbles.csv"

def main():
    network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
    )

    user = network.get_user(USER)
    tracks= user.get_recent_tracks(limit=None)
    print(tracks)

    print(f"Scraped {len(tracks)} scrobbles from user {USER}")
    print("Formatting data...")

    tracks = [{"title": unicode(x[0].title).encode("utf-8"),
               "artist": unicode(x[0].artist.name).encode("utf-8"),
               "album": unicode(x.album).encode("utf-8"),
               "playback_date": unicode(x.playback_date).encode("utf-8"),
               "timestamp": unicode(x.timestamp).encode("utf-8")} for x in tracks]

    print(f"Writing to {FILENAME}")
    csv_keys = tracks[0].keys()
    with open(FILENAME, 'w', newline='') as f:
        writer = DictWriter(f, csv_keys)
        writer.writeheader()
        writer.writerows(tracks)

if __name__ == "__main__":
    main()

