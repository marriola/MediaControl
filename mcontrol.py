from gi.repository import Gtk, Gdk
#gi.require_version("Gtk", "3.0")

#import gtk

class MediaControl(Gtk.Window):
    def __init__(self):
        self.gladefile = "mcontrol.glade"
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)

        self.window = self.glade.get_object("winMControl")
        self.labels = [ self.glade.get_object("labelSymbol"), self.glade.get_object("labelNumber") ]
        self.labels += map(lambda x: self.glade.get_object("label" + x), list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

        css = Gtk.CssProvider()
        display = Gdk.Display.get_default()
        screen = Gdk.Display.get_default_screen(display)

        Gtk.StyleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        css.load_from_path("mcontrol.css")

        self.window.show_all()

    def winMControl_hide(self, sender):
        Gtk.main_quit()
        

if __name__ == "__main__":
    win = MediaControl()
    Gtk.main()
