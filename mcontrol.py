import functools
from gi.repository import Gtk, Gdk, GLib
from library import Library
from models import Artist, Album
import os
from RB import RB


################################################################################

ENV_LIBRARY = os.environ["MUSIC_LIBRARY"] if "MUSIC_LIBRARY" in os.environ else None
LIBRARY_DIRECTORIES = (map(lambda x: x if x.endswith("/") else x + "/", ENV_LIBRARY.split(";")) if ENV_LIBRARY else [ "./" ])
MUSIC_LIBRARY = "musiclib"
ICON_SIZE = 16


################################################################################

def seconds_to_min_seconds(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return "{:02d}:{:02d}".format(int(minutes), int(seconds))


def homogenous_artist(track_list):
    first = track_list[0].artist
    return functools.reduce(lambda acc, val: acc and val.artist.upper() == first.upper(), track_list, True)


def homogenous_album(track_list):
    first = track_list[0].album
    return functools.reduce(lambda acc, val: acc and val.album.upper() == first.upper(), track_list, True)


class MediaControl(Gtk.Window):
    def __init__(self, library):
        self.timer = None
        self.ignore = False
        self.playing = False
        self.library = library
        for dir in LIBRARY_DIRECTORIES:
            print("scanning " + dir)
            self.library.scan(dir)
        
        Gtk.IconTheme.add_builtin_icon("band16", 16, Gtk.Image.new_from_file("band16.png").get_pixbuf())

        self.gladefile = "mcontrol.glade"
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)

        self.window = self.glade.get_object("winMControl")
        self.window.resize(480, 320)
        self.window.set_resizable(False)

        self.scaleTime = self.glade.get_object("scaleTime")
        self.lblTime = self.glade.get_object("lblTime")
        
        self.btnSymbol = self.glade.get_object("btnSymbol")
        self.btnNumber = self.glade.get_object("btnNumber")
        self.buttons = map(lambda x: self.glade.get_object("btn" + x), list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

        self.tglAlbum = self.glade.get_object("tglAlbum")
        self.tglBand = self.glade.get_object("tglBand")
        self.filter_mode = self.tglAlbum.get_active()
        
        self.btnPlayPause = self.glade.get_object("btnPlayPause")
        self.imgPlay = self.glade.get_object("imgPlay")
        self.imgPause = self.glade.get_object("imgPause")

        self.view = False
        self.scrolled_window = self.glade.get_object("scrolledwindow1")
        self.track_list = self.glade.get_object("tvTrackList")
        self.track_store = self.glade.get_object("trackStore")

        self.track_list_columns = [Gtk.TreeViewColumn("Track", Gtk.CellRendererText(), text=0),
                                   Gtk.TreeViewColumn("Title", Gtk.CellRendererText(), text=1),
                                   Gtk.TreeViewColumn("Album", Gtk.CellRendererText(), text=2),
                                   Gtk.TreeViewColumn("Year", Gtk.CellRendererText(), text=3),
                                   Gtk.TreeViewColumn("Artist", Gtk.CellRendererText(), text=4)]

        for c in self.track_list_columns:
            self.track_list.append_column(c)
        
        self.icon_view = self.glade.get_object("ivArtistAlbum")
        self.icon_view.set_pixbuf_column(0)
        self.icon_view.set_markup_column(1)
        self.artist_store = self.glade.get_object("artistStore")
        self.do_filter()
        
        css = Gtk.CssProvider()
        display = Gdk.Display.get_default()
        screen = Gdk.Display.get_default_screen(display)

        Gtk.StyleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        css.load_from_path("mcontrol.css")

        self.window.show_all()
        self.window.present()


    def set_view(self, track_list):
        if self.view == track_list:
            return

        self.view = track_list
        if self.view == True:
            self.scrolled_window.remove(self.icon_view)
            self.scrolled_window.add(self.track_list)

            self.ignore = True
            self.tglBand.set_active(False)
            self.ignore = True
            self.tglAlbum.set_active(False)
            
        else:
            self.scrolled_window.remove(self.track_list)
            self.scrolled_window.add(self.icon_view)
        

    def set_filter_mode(self, setting):
        self.ignore = True
        self.tglAlbum.set_active(setting)
        self.ignore = True
        self.tglBand.set_active(not setting)
        self.filter_mode = setting
        

    def toggle_filter_mode(self, button):
        #print("toggle filter")
        if self.ignore:
            self.ignore = False
            return
        
        self.ignore = True
        if button == self.tglBand:
            self.tglAlbum.set_active(not button.get_active())
        else:
            self.tglBand.set_active(not button.get_active())

        self.filter_mode = self.tglAlbum.get_active()
        self.do_filter()


    def set_timer(self):
        self.timer_suspended = False
        self.timer = GLib.timeout_add_seconds(1, lambda x: self.increment_scroll(x), None)


    def update_time(self):
        time_in = self.scaleTime.get_value()
        time_total = self.scaleTime.get_adjustment().get_upper()
        self.lblTime.set_label("{}/{}".format(seconds_to_min_seconds(time_in), seconds_to_min_seconds(time_total)))
            
        
    def increment_scroll(self, data):
        self.scaleTime.set_value(self.scaleTime.get_value() + 1)
        self.update_time()
        return True


    def toggle_playing(self):
        self.playing = not self.playing
        if self.playing:
            self.set_timer()
        self.btnPlayPause.set_image(self.imgPause if self.playing else self.imgPlay)

    
    def btnPlayPause_clicked(self, button):
        self.toggle_playing()


    def do_filter(self, filter=None, album=None):
        #print(self.filter_mode)
        if album:
            self.library.build_track_list(self.track_store, filter, album)

            self.track_list_columns[4].set_visible(not homogenous_artist(self.library.track_store_list))
            self.track_list_columns[2].set_visible(not homogenous_album(self.library.track_store_list))

            self.set_view(True)
        elif self.filter_mode:
            self.library.build_albums_store(self.artist_store, filter)
            self.set_view(False)
        else:
            self.library.build_artists_store(self.artist_store, filter)
            self.set_view(False)


    def filter_all(self, button):
        self.do_filter()
        

    def filter_number(self, button):
        self.do_filter(lambda x: x.title[0].isdigit() if hasattr(x, "title") else x.name[0].isdigit())
        

    def filter_symbol(self, button):
        self.do_filter(lambda x: (not x.title[0].isalpha() and not x.title[0].isdigit()) if hasattr(x, "title") else
                                 (not x.name[0].isalpha() and not x.name[0].isdigit()))
        
    
    def filter_letter(self, button):
        filter_char = button.get_label()
        self.do_filter(filter_char)


    def track_tapped(self, tree_view, path, column):
        index = int(path.to_string())
        RB.play_file(self.library.track_store_list[index].path)
        self.toggle_playing()
        

    def item_activated(self, iconview, path):
        index = int(path.to_string())
        if self.filter_mode:
            album = self.library.albums_store[index]
            #print("tap album: " + album.artist + " - " + album.title)
            self.do_filter(filter=album.artist, album=album.title)
        else:
            artist = self.library.artists_store[index]
            #print("tap artist: " + artist.name)
            self.set_filter_mode(True)
            self.do_filter(self.library.artists_store[index].name)
    
        
    def scaleTime_value_changed(self, widget):
        if not self.timer_suspended:
            RB.begin_seek()
            GLib.Source.remove(self.timer)
            self.timer = None
            self.timer_suspended = True

        self.update_time()


    def scaleTime_key_release(self, widget, event):
        if self.timer_suspended:
            self.set_timer()
            RB.end_seek(self.scaleTime.get_value())


    def scaleTime_button_release(self, widget, event):
        if self.timer_suspended:
            self.set_timer()
            RB.end_seek(self.scaleTime.get_value())
            

    def winMControl_hide(self, sender):
        self.library.save(MUSIC_LIBRARY)
        Gtk.main_quit()


################################################################################

if __name__ == "__main__":
    library = Library(ICON_SIZE)
    library.load(MUSIC_LIBRARY)
    #RB.start()
    win = MediaControl(library)
    Gtk.main()
