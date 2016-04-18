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
    def __init__(self, artist, album, year, track, title, genre):
        self.artist = artist
        self.album = album
        self.year = year
        self.track = track
        self.title = title
        self.genre = genre
