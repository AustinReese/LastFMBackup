from os import environ
from dotenv import load_dotenv
from LastFmApiDriver import LastFmApiDriver

load_dotenv(override=True)

API_KEY = environ["LASTFM_API_KEY"]
API_SECRET = environ["LASTFM_SHARED_SECRET"]
USER = environ["USER"]
FILENAME = f"./{USER}_scrobbles.csv"


def main():
    driver = LastFmApiDriver(API_KEY, API_SECRET)
    driver.save_recent_tracks(USER)


if __name__ == "__main__":
    main()

