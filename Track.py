import sqlite3

class Track:

    def __init__(self):
        pass

    def __init__(self,
                 track_title,
                 track_mbid,
                 artist_name,
                 artist_mbid,
                 album_name,
                 album_mbid,
                 duration,
                 unique_listeners,
                 total_playcount,
                 tags,
                 streamed_timestamp,
                 streamed_datetime
                 ):

        #Remove recording descriptions from tracks, necessary for some titles from Spotify
        bad_title_strings = [" remaster", " version", " mix", " mono", " live", " alternate", " demo", " including", " edit"]
        if '-' in track_title and any(bad_str in track_title.lower() for bad_str in bad_title_strings):
            track_title = "-".join(track_title.split('-')[:-1]).strip()
        self.track_title = track_title
        self.track_mbid = track_mbid
        self.artist_name = artist_name
        self.artist_mbid = artist_mbid
        self.album_name = album_name
        self.album_mbid = album_mbid
        self.duration = int(duration) / 1000
        self.unique_listeners =unique_listeners
        self.total_playcount = total_playcount
        self.tags = tags
        self.streamed_timestamp = streamed_timestamp
        self.streamed_datetime = streamed_datetime

    def save(self, user):
        conn = sqlite3.connect("main.db")
        curs = conn.cursor()
        to_insert = (self.track_title, self.track_mbid, self.artist_name, self.artist_mbid, self.album_name, self.album_mbid,
                     self.duration, self.unique_listeners, self.total_playcount, self.tags, self.streamed_timestamp, self.streamed_datetime)
        sql_insert = f"INSERT INTO lastfm_tracks_{user}(title, musicbrainz_id, artist, artist_musicbrainz_id, album, album_musicbrainz_id, \
                     duration, listeners, playcount, tags, played_timestamp, played_date) \
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?);"

        curs.execute(sql_insert, to_insert)
        conn.commit()
        conn.close()

    def __str__(self):
        return f"{self.track_title}\n{self.artist_name}\n{self.album_name}\nPlayed {self.streamed_datetime}\n{self.duration // 60} minutes {self.duration % 60} seconds\n" \
               f"{self.unique_listeners} unique listeners\n{self.total_playcount} total plays\nTags: {self.tags}"
