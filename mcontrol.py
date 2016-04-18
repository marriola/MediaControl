import functools
from gi.repository import Gtk, Gdk
from library import Library
from models import Artist, Album
from RB import RB


################################################################################

MUSIC_LIBRARY = "musiclib"
ICON_SIZE = 16


################################################################################
        
class MediaControl(Gtk.Window):
    def __init__(self, library):
        self.ignore = False
        self.playing = False
        self.library = library
        self.library.scan("/home/minebox/")
        
        self.gladefile = "mcontrol.glade"
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)

        self.window = self.glade.get_object("winMControl")
        self.window.resize(480, 320)
        self.window.set_resizable(False)

        self.btnSymbol = self.glade.get_object("btnSymbol")
        self.btnNumber = self.glade.get_object("btnNumber")
        self.buttons = map(lambda x: self.glade.get_object("btn" + x), list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

        self.tglAlbum = self.glade.get_object("tglAlbum")
        self.tglBand = self.glade.get_object("tglBand")
        self.filter_mode = self.tglAlbum.get_active()
        
        self.btnPlayPause = self.glade.get_object("btnPlayPause")
        self.imgPlay = self.glade.get_object("imgPlay")
        self.imgPause = self.glade.get_object("imgPause")

        self.icon_view = self.glade.get_object("iconview3")
        self.icon_view.set_pixbuf_column(0)
        #self.icon_view.set_text_column(1)
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
            
        
    def btnPlayPause_clicked(self, button):
        self.playing = not self.playing
        self.btnPlayPause.set_image(self.imgPause if self.playing else self.imgPlay)


    def do_filter(self, filter=None):
        #print(self.filter_mode)
        if self.filter_mode:
            self.library.build_albums_store(self.artist_store, filter)
        else:
            self.library.build_artists_store(self.artist_store, filter)


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
