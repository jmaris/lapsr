#!/usr/bin/python
from __future__ import division
from gi.repository import Gtk
import shutil
import os
import subprocess
import linecache
import gobject
class Handler:

#Exit the look on program closure
    def onDeleteWindow(self, *args):
        print "EXIT";
        Gtk.main_quit(*args)

#lapse complete, quit program
    def quit(self, *args):
        exit()

#Open and close the about dialog
    def openAbout(self, *args):
        print "Test";
        about.show_all()

    def hideAbout(self, *args):
        print "Test";
        about.hide()

#wiz4 display currently for debugging
    def display4(self, *args):
        wiz4.show_all()

#open and close the camera wizards first screen.
    def openWiz1(self, *args):
        window.hide()
        wiz1.show_all()

    def closeWiz1(self, *args):
        wiz1.hide()
        window.show_all()

#retry or cancel from the error screen
    def retry(self, *args):
        wiz1error.hide()
        wiz1.show_all()

    def wiz1errorclose(self, *args):
        wiz1error.hide()
        window.show_all()

#Open and close the camera wizards second screen
    def openWiz2(self, *args):
        wiz2.show_all()

    def closeWiz2(self, *args):
        wiz2.hide()
        window.show_all()

#List detected Cameras and prepare temp directory for images
    def listcams(self, *args):
        wiz1.hide()
        path = "/tmp/lapsr"
        print "Creating or emptying directory ",path
        if os.path.exists(path):shutil.rmtree(path)
        if not os.path.exists(path): os.mkdir(path)
        os.chdir( path )
        print "working directory set to ",path
        print "detecting cameras"
        output = subprocess.check_output("gphoto2 --auto-detect>cameras", shell=True)
        num_lines = sum(1 for line in open('cameras'))
        if num_lines==2:
            print "No cameras detected"
            wiz1.hide()
            wiz1error.show_all()
        else:
            camera = linecache.getline('cameras', 3)
            print camera," detected"
            cameraid.set_text(camera)
            wiz2.show_all()

#allows for lapse cancelation after next shot
    def cancellapse(self, *args):
        completed=1
        print "cancelation request received"
        subprocess.check_output("killall gphoto2", shell=True)
        if os.path.exists(path):shutil.rmtree(path)
        wiz3.hide()

#lapse postprocessing

    def postprocess(self, *args):
        print "starting postprocessing"
        wiz4.hide()
        savelps = checkbutton1.get_active()
        savevid = checkbutton2.get_active()
        print savelps
        print savevid
        if savelps == True:
            print "Saving a lapse file"
            subprocess.check_output("tar cvzf /tmp/lapse.tar.gz /tmp/lapsr", shell=True)
        if savevid == True:
            print "saving a video"
            path = "/tmp/lapsr"
            os.chdir( path )
            framerate = spin3.get_value_as_int()
            subprocess.check_output("ls -1tr | grep -v files.txt > files.txt", shell=True)
            framerate = str(framerate)
            framerate = 'fps='+framerate
            proc2 = subprocess.Popen(['mencoder','-idx','-nosound','-noskip','-ovc','lavc','-lavcopts','vcodec=mjpeg','-o','output.avi','-mf',framerate,'mf://@files.txt'],cwd='/tmp/lapsr',stdout=subprocess.PIPE)
            completed2=0
            while completed2 == 0:
                line = proc2.stdout.readline()
                if line != '':
                    print "[output]",line
                else:
                    completed2 = 1
            print "done"
            wiz5.show_all()

# take the information and run the lapse
    def startlapse(self, *args):
        wiz2.hide()
        frames = spin1.get_value_as_int()
        delay = spin2.get_value_as_int()
        print frames, " frames will be shot"
        print "with ", delay, " seconds between each shot"
        wiz2.hide()
        wiz3.show_all()
        proc = subprocess.Popen(['gphoto2','--capture-image-and-download','-F',str(frames),'-I',str(delay)],stdout=subprocess.PIPE)
        print "starting processing loop WARNING : No error detection supported, if focus fails the app will hang"
        completed = 0
        while completed == 0:
            if Gtk.events_pending():print "Rendering Progress bar updates"
            while Gtk.events_pending():
                Gtk.main_iteration()
            line = proc.stdout.readline()
            if line != '':
                if line.find("Capturing frame #") != -1:
                    print "[debug] progress found"
                    newstr = line.replace("Capturing frame #","")
                    newstr = newstr.split('...', 1)[0]
                    newstr = newstr.split('/', 1)
                    newstr = (int(newstr[0])/int(newstr[1]))      
                    progressbar1.set_fraction(newstr)
                    print "[PROGRESS]", line
            else:
                print "complete"
                completed = 1
        wiz4.show_all()
        wiz3.hide()


#GTK and handler setup
builder = Gtk.Builder()
builder.add_from_file("lapsr.glade")
builder.connect_signals(Handler())

#"naming" windows and objects for callback/signal
#windows
about = builder.get_object("about")
wiz1 = builder.get_object("wiz1")
wiz2 = builder.get_object("wiz2")
wiz3 = builder.get_object("wiz3")
wiz4 = builder.get_object("wiz4")
wiz5 = builder.get_object("wiz5")
#objects
cameraid = builder.get_object("label10")
wiz1error = builder.get_object("wiz1error")
spin1 = builder.get_object("spinbutton1")
spin2 = builder.get_object("spinbutton2")
progressbar1 = builder.get_object("progressbar1")
spin3 = builder.get_object("spinbutton3")
checkbutton1 = builder.get_object("checkbutton1")
checkbutton2 = builder.get_object("checkbutton2")

#display, window 1 and enter the loop
window = builder.get_object("window1")
window.show_all()
Gtk.main()
