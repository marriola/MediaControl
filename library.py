import gzip
import pickle
from mutagen.id3 import ID3
import os
import functools
import re
from gi.repository import Gtk, Gdk
from models import Artist, Album, Track


RE_MEDIA = re.compile(".*\.mp3")
NUMERIC = re.compile("(\d+)")


class Library(object):
    def __init__(self, iconSize):
        self.ICON_SIZE = iconSize
        self.files = set()
        self.artists = dict()


    def save(self, path):
        try:
            f = gzip.open(path, "wb")
            p = pickle.Pickler(f)
            p.dump(self.files)
            p.dump(self.artists)
            f.close()
            return True
            
        except:
            return False

        
    def load(self, path):
        try:
            f = gzip.open(path, "rb")
            up = pickle.Unpickler(f)
            self.files = up.load()
            self.artists = up.load()
            f.close()
            print("loaded " + str(len(self.files)) + " tracks")
            return True
        
        except Exception as e:
            print("load:" + e.__str__())
            return False
        

    def populate(self, path):
        n = 0
        
        for root, dirs, files in os.walk(path):
            for file in files:
                if RE_MEDIA.match(file):
                    if self.catalog(root + file):
                        n += 1

        print("catalogged " + str(n) + " files")


    def catalog(self, path):
        if path in self.files:
            return False

        file = ID3(path)
        tracks = Library.get_value(file.getall("TRCK"))
        titles = Library.get_value(file.getall("TIT2"))
        albums = Library.get_value(file.getall("TALB"))
        artists = Library.get_value(file.getall("TPE1"))
        years = Library.get_value(file.getall("TDRC"))
        genres = Library.get_value(file.getall("TCON"))

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
        
        self.files.add(path)
        track = Track(path, artist, album, year, track, title, genre)

        if artist not in self.artists:
            self.artists[artist] = Artist(artist, genre)
            
        if album not in self.artists[artist].albums:
            self.artists[artist].albums[album] = Album(artist, album, genre, year)

        self.artists[artist].albums[album].tracks.append(track)

        #print("catalogged " + artist + " - " + album + " - " + title + " (" + str(year) + ")")
        return True


    @staticmethod
    def get_value(frames):
        if len(frames) == 0:
            return None
        return frames[0].text[0]
        
            
    def build_artists_store(self, store, letter=None):
        if type(letter) is str:
            artists = filter(lambda x: x.name[0].upper() == letter.upper(), map(lambda x: x[1], self.artists.items()))
        elif callable(letter):
            artists = filter(letter, map(lambda x: x[1], self.artists))
        else:
            artists = map(lambda x: x[1], self.artists.items())
            
        store.clear()
        for artist in artists:
            store.append(None, self.create_artist(artist))

            
    def build_albums_store(self, store, letter=None):
        if letter == None:
            filter_fun = lambda x: True
        elif callable(letter):
            filter_fun = letter
        elif type(letter) is str:
            filter_fun = lambda x: x.title[0].upper() == letter.upper()
        else:
            filter_fun = None
        
        #albums = filter(filter_fun, reduce(lambda acc, val: dict(({} if acc == None else acc), **val.albums), self.artists, {}))
        albums = filter(filter_fun,
                        reduce(lambda acc, val: ([] if acc == None else acc) + map(lambda x: x[1], val.albums.items()),
                               map(lambda x: x[1], self.artists.items()),
                               []))
        albums.sort(key=lambda x: x.title)
        
        store.clear()
        for album in albums:
            #print("adding " + album.artist + " - " + album.title)
            store.append(None, self.create_album(album))

            
    def create_album(self, album):
        return [Gtk.IconTheme.get_default().load_icon("media-optical", self.ICON_SIZE, 0),
                album.__str__()]

    
    def create_artist(self, artist):
        return [Gtk.IconTheme.get_default().load_icon("applications-multimedia", self.ICON_SIZE, 0),
                artist.name]
