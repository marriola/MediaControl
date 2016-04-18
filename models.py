import re

NUMERIC = re.compile("(\d+)")


class Artist(object):
    def __init__(self, name, genres):
        self.albums = dict()
        self.name = name
        self.genres = genres

class Album(object):
    def __init__(self, artist, title, genres, year):
        self.artist = artist
        self.title = title
        self.genres = genres
        self.year = year
        self.tracks = []


    def __str__(self):
        return self.artist + "\n" + self.title + "\n" + self.year.__str__()


class Track(object):
    def __init__(self, path, artist, album, year, track, title, genre):
        self.path = path
        self.artist = artist
        self.album = album
        self.year = year
        self.track = track
        self.title = title
        self.genre = genre

    @staticmethod
    def from_id3(path, id3):
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
            track = -1    
        
        title = titles if titles else "<no title>"
        album = albums if albums else "<no album>"
        artist = artists if artists else "<no artist>"
        genre = genres if genres else "<no genre>"
        year = years.year if years else 0

        return Track(path, artist, album, year, track, title, genre)


    @staticmethod
    def get_value(frames):
        if len(frames) == 0:
            return None
        return frames[0].text[0]
        
