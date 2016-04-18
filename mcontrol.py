import functools
from gi.repository import Gtk, Gdk
from library import Library
from models import Artist, Album


################################################################################
        
class MediaControl(Gtk.Window):
    def __init__(self, library):
        self.playing = False
        self.library = library

        self.gladefile = "mcontrol.glade"
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)

        self.window = self.glade.get_object("winMControl")
        self.labels = [ self.glade.get_object("labelSymbol"), self.glade.get_object("labelNumber") ]
        self.labels += map(lambda x: self.glade.get_object("label" + x), list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

        self.btnPlayPause = self.glade.get_object("btnPlayPause")
        self.imgPlay = self.glade.get_object("imgPlay")
        self.imgPause = self.glade.get_object("imgPause")

        self.icon_view = self.glade.get_object("iconview3")
        self.icon_view.set_pixbuf_column(0)
        self.icon_view.set_text_column(1)
        self.artist_store = self.glade.get_object("artistStore")
        self.library.build_albums_store(self.artist_store)
        
        css = Gtk.CssProvider()
        display = Gdk.Display.get_default()
        screen = Gdk.Display.get_default_screen(display)

        Gtk.StyleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        css.load_from_path("mcontrol.css")

        self.window.show_all()
        
        
    def btnPlayPause_clicked(self, button):
        self.playing = not self.playing
        self.btnPlayPause.set_image(self.imgPause if self.playing else self.imgPlay)

        
    def winMControl_hide(self, sender):
        Gtk.main_quit()


################################################################################

if __name__ == "__main__":
    library = Library.load("library")
    win = MediaControl(library)
    Gtk.main()
