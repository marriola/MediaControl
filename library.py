import functools
from gi.repository import Gtk, Gdk
import gzip
from models import Artist, Album, Track, AllAlbums
import pickle
import os


def dbg(data):
    print("*** dbg: ", end='')
    print(data)
    return data

def matches(field, goal):
    return goal == "*" or field.upper() == goal.upper()

def dict_to_list(dict):
    return list(map(lambda x: x[1], dict.items()))


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
        

    def scan(self, path):
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


    def all_albums(self, artist):
        return functools.reduce(lambda acc, val: ([] if acc == None else acc) + (dict_to_list(val.albums) if matches(val.name, artist) else []), dict_to_list(self.artists), [])

    def all_tracks(self, album_filter, albums):
        return functools.reduce(lambda acc, val: ([] if acc == None else acc) + (sorted(val.tracks, key=lambda x: x.track) if matches(val.title, album_filter) else []), albums, [])

    def build_track_list(self, store, artist, album):
        filter_fun = lambda x: x.artist.upper() == artist.upper() and x.album.upper() == album.upper()
        albums = self.all_albums(artist)
        self.track_store_list = self.all_tracks(album, albums)
        
        store.clear()
        for track in self.track_store_list:
            store.append(None, self.create_track(track))


    def create_track(self, track):
        return [track.track, track.title, track.album, track.year, track.artist]
        

    # list_filter type
    # ------------------------------
    # None              No filter
    # function          The artist object is passed as a parameter for each artist. Returns True if the artist should be included.
    # string (1 char)   Artists beginning with that letter are filtered
    def build_artists_store(self, store, list_filter=None):
        if type(list_filter) is str:
            filter_fun = lambda x: x.name[0].upper() == list_filter.upper()
        elif callable(list_filter):
            filter_fun = list_filter
        else:
            filter_fun = lambda x: True

        self.artists_store = [x for x in dict_to_list(self.artists) if filter_fun(x)]
        self.artists_store.sort(key=lambda x: x.name)
        
        store.clear()
        for artist in self.artists_store:
            store.append(None, self.create_artist(artist))

            
    # list_filter type
    # ------------------------------
    # None              No filter
    # function          The album object is passed as a parameter for each album. Returns True if the album should be included.
    # string (1 char)   Albums beginning with that letter are filtered
    # string (2+ chars) Albums by that artist are shown
    def build_albums_store(self, store, list_filter=None):
        artist_filter = False
        
        if list_filter == None:
            filter_fun = lambda x: True
        elif callable(list_filter):
            filter_fun = list_filter
        elif type(list_filter) is str or type(list_filter) is unicode:
            if len(list_filter) == 1:
                filter_fun = lambda x: x.title[0].upper() == list_filter.upper()
            else:
                artist_filter = True
                filter_fun = lambda x: x.artist.upper() == list_filter.upper()
        else:
            filter_fun = None
        
        self.albums_store = [x for x in
                        functools.reduce(lambda acc, val: ([] if acc == None else acc) + dict_to_list(val.albums),
                               dict_to_list(self.artists),
                               []) if filter_fun(x)]
        self.albums_store.sort(key=lambda x: x.year)

        if artist_filter:
            self.albums_store = [AllAlbums(list_filter)] + self.albums_store
        
        store.clear()
        for album in self.albums_store:
            store.append(None, self.create_album(album))

            
    def create_album(self, album):
        return [Gtk.IconTheme.get_default().load_icon("media-optical", self.ICON_SIZE, 0),
                album.__str__()]

    
    def create_artist(self, artist):
        return [Gtk.IconTheme.get_default().load_icon("band16", self.ICON_SIZE, 0),
                artist.__str__()]
