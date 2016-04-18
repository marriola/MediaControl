import functools
from gi.repository import Gtk, Gdk
import gzip
from models import Artist, Album, Track
import pickle
import os


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
                if ((root + file) not in self.files and
                    file.lower().endswith(".mp3") and
                    self.catalog_mp3(root + file)):
                    n += 1

        print("catalogged " + str(n) + " new tracks")


    def catalog(self, track):
        if track.artist not in self.artists:
            self.artists[track.artist] = Artist(track.artist, track.genre)

        if track.album not in self.artists[track.artist].albums:
            self.artists[track.artist].albums[track.album] = Album(track.artist, track.album, track.genre, track.year)

        self.artists[track.artist].albums[track.album].tracks.append(track)

        print("catalogged " + track.artist + " - " + track.album + " - " + track.title + " [" + str(track.length) + "] (" + str(track.year) + ")")
        return True
        

    def catalog_mp3(self, path):
        if path in self.files:
            return False

        try:
            track = Track.from_file(path)
            self.files.add(path)
        except Exception as e:
            print("catalog failed (" + path + "): " + e.__str__())

        return self.catalog(track)


    def build_artists_store(self, store, letter=None):
        if type(letter) is str:
            filter_fun = lambda x: x.name[0].upper() == letter.upper()
        elif callable(letter):
            filter_fun = letter
        else:
            filter_fun = lambda x: True

        artists = filter(filter_fun, map(lambda x: x[1], self.artists.items()))
            
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
