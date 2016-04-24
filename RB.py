import dbus
import subprocess

db = dbus.SessionBus()
position_before_seek = None
proxy_obj = None
rhythmbox = None
player = None
props = None


def set(interface, prop, value):
    if player == None:
        return
    props.Set('org.mpris.MediaPlayer2.' + interface, prop, value)

    
def get(interface, prop):
    if player == None:
        return None
    return props.Get('org.mpris.MediaPlayer2.' + interface, prop)


def start():
    global proxy_obj, rhythmbox, player, props
    subprocess.call("rhythmbox-client")
    proxy_obj = db.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
    player = dbus.Interface(proxy_obj, 'org.mpris.MediaPlayer2.Player')
    playlists = dbus.Interface(proxy_obj, 'org.mpris.MediaPlayer2.Playlists')
    rhythmbox = dbus.Interface(proxy_obj, 'org.mpris.MediaPlayer2')
    props = dbus.Interface(proxy_obj, 'org.freedesktop.DBus.Properties')

    
def quit():
    if rhythmbox:
        rhythmbox.Quit()

        
def get_playlists():
    if playlists == None:
        return None
    return playlists.GetPlaylists(0, 9999, "Alphabetical", False)



def get_play_queue():
    if playlists == None:
        return None
    return


def play_pause():
    if player == None:
        return
    player.PlayPause()

    
def play():
    if player == None:
        return
    player.Play()

    
def pause():
    if player == None:
        return
    player.Pause()

    
def stop():
    if player == None:
        return
    player.Stop()

    
def play_file(file):    
    if player == None:
        return
    player.OpenUri("file://" + file)

    
def seek(seconds):
    if player == None:
        return
    player.Seek(seconds * 1000000)

    
def set_volume(level):
    if player == None:
        return
    set("Player", "Volume", level / 100)

    
def get_volume():
    if player == None:
        return None
    return get("Player", "Volume") * 100


def get_position():
    if player == None:
        return None
    return get("Player", "Position") / 1000000


def next():
    if player == None:
        return
    player.Next()

    
def previous():
    if player == None:
        return
    player.Previous()

    
def begin_seek():
    global position_before_seek
    if player == None:
        return
    position_before_seek = int(get_position())
    pause()


def end_seek(time):
    global position_before_seek
    if player == None:
        return
    position_now = time
    print("seek to", position_now, "from", position_before_seek)
    seek(position_now - position_before_seek)
    position_before_seek = None
    play()
