class Artist(object):
    def __init__(self, name, genres):
        self.albums = []
        self.name = name
        self.genres = genres

class Album(object):
    def __init__(self, artist, title, genres, year):
        self.artist = artist
        self.title = title
        self.genres = genres
        self.year = year
