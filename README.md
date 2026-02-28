# LastFMBackup

Save all scrobbles from any LastFM user.

*Please note that I have only tested this application on my own LastFM library, errors are likely to occur with other, larger libraries. I encourage you to report these issues or create pull requests with fixes, see more information under [Contributing](#contributing)*

## Installation

Install required libraries

```bash
pip install -r requirements.txt
```

## Usage

Obtain an API key and secret from [LastFM](https://www.last.fm/api/account/create)

Set necessary environment variables (or set in .env)

```bash
export LASTFM_API_KEY="<your_lastfm_api_key>"
export LASTFM_SHARED_SECRET="<your_lastfm_shared_secret>"
export USER="<lastfm_username_to_backup>"
```

Simply run Main.py and the download will begin

```bash
python3 Main.py
```

Data is stored in main.db, located in the directory the project was run

## License
[MIT](https://choosealicense.com/licenses/mit/)
