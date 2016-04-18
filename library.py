import functools
from gi.repository import Gtk, Gdk
from models import Artist, Album

class Library(object):
    def __init__(self):
        self.artists = []

    @staticmethod
    def load(path):
        lib = Library()
        for i in range(0, 10):
            x = Artist("artist " + i.__str__(), "Rock")
            for k in range(0, 10):
                y = Album(x.name, "album " + k.__str__(), "Rock", 2000 + k)
                x.albums.append(y)
            
            lib.artists.append(x)

        return lib
        
    def build_artists_store(self, store, letter=None):
        if letter:
            artists = filter(lambda x: x.name[0] == letter, self.artists)
        else:
            artists = self.artists
            
        store.clear()
        for artist in self.artists:
            store.append(None, [Gtk.IconTheme.get_default().load_icon("applications-multimedia", 64, 0), artist.name])

    def build_albums_store(self, store, letter=None):
        if letter:
            artists = filter(lambda x: x.name[0] == letter, self.artists)
        else:
            artists = self.artists
            
        albums = reduce(lambda acc, val: ([] if acc == None else acc) + val.albums, self.artists, [])
        albums.sort(key=lambda x: x.title)
        store.clear()
        for album in albums:
            #print("adding " + album.artist + " - " + album.title)
            store.append(None, [Gtk.IconTheme.get_default().load_icon("applications-multimedia", 64, 0), album.artist + "\n" + album.title])
