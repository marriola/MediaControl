from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import re

NUMERIC = re.compile("(\d+)")


def pluralize(n, x):
    if n == 1:
        return str(n) + " " + x
    else:
        return str(n) + " " + x + "s"


class Artist(object):
    def __init__(self, name, genres):
        self.albums = dict()
        self.name = name
        self.genres = genres

    def __str__(self):
        return u"{}\n<i>{}</i>".format(self.name, pluralize(len(self.albums.keys()), "album"))
    

class Album(object):
    def __init__(self, artist, title, genres, year):
        self.artist = artist
        self.title = title
        self.genres = genres
        self.year = year
        self.tracks = []


    def __str__(self):
        return u"{}\n<b>{}</b>\n{}".format(self.title, self.artist, self.year.__str__())


class AllAlbums(Album):
    def __init__(self, artist="*"):
        super(AllAlbums, self).__init__(artist, "*", "*", None)


    def __str__(self):
        return "<i>All albums</i>"
    

class Track(object):
    def __init__(self, path, length, artist, album, year, track, title, genre):
        self.path = path
        self.length = length
        self.artist = artist.strip() if artist else artist
        self.album = album.strip() if album else album
        self.year = year
        self.track = track
        self.title = title.strip() if title else title
        self.genre = genre.strip() if genre else genre


    @staticmethod
    def from_file(path):
        mp3 = MP3(path)
        length = mp3.info.length

        id3 = ID3(path)
        tracks = Track.get_value(id3.getall("TRCK"))
        titles = Track.get_value(id3.getall("TIT2"))
        albums = Track.get_value(id3.getall("TALB"))
        artists = Track.get_value(id3.getall("TPE1"))
        years = Track.get_value(id3.getall("TDRC"))
        genres = Track.get_value(id3.getall("TCON"))

        if tracks:
            m = NUMERIC.match(tracks)
            if m:
                track = int(m.group(0))
        else:
            track = None
        
        title = titles if titles else "<no title>"
        album = albums if albums else "<no album>"
        artist = artists if artists else "<no artist>"
        genre = genres if genres else "<no genre>"
        year = years.year if years else None

        return Track(path, length, artist, album, year, track, title, genre)


    @staticmethod
    def get_value(frames):
        if len(frames) == 0:
            return None
        return frames[0].text[0]
        
