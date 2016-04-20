import subprocess

class RB(object):
    @staticmethod
    def command(*args):
        if len(args) > 0:
            params = ["--" + args[0]] + list(args)[1:]
        else:
            params = []
            
        subprocess.call(["rhythmbox-client"] + params)

    @staticmethod
    def start():
        RB.command()
        #RB.command("clear-queue")
        
    @staticmethod
    def play_pause():
        RB.command("play-pause")

    @staticmethod
    def play():
        RB.command("play")

    @staticmethod
    def pause():
        RB.command("pause")
        
    @staticmethod
    def play_file(file):
        RB.command("clear-queue")
        RB.command("play-uri=" + file)

    @staticmethod
    def seek(seconds):
        RB.command("seek", seconds.__str__())

    @staticmethod    
    def volume(level):
        RB.command("set-volume", level.__str__())

    @staticmethod
    def next():
        RB.command("next")

    @staticmethod
    def previous():
        RB.command("previous")

    @staticmethod
    def enqueue(tracks):
        RB.command("enqueue", *tracks)


    @staticmethod
    def begin_seek():
        RB.command("pause")


    @staticmethod
    def end_seek(time):
        RB.command("seek", str(time))
        RB.command("play")
