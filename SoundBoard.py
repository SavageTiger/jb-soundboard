#!/usr/bin/env python

import sys, os

from gi.repository import Gtk

import modSoundBoardXML

class wndMain:

    soundBoardXML = None

    def __init__(self):
        # Render the main window

        self.glade = Gtk.Builder()
        self.glade.add_from_file("GUI.glade")
        self.glade.get_object("wndMain").show_all()
        self.glade.get_object("wndMain").connect("delete-event", Gtk.main_quit)


        # Fill the soundboards dropdpown and bind events
        dropdown = self.glade.get_object("cmbSoundboard")

        self.soundBoardXML = modSoundBoardXML.SoundboardXML()
        self.soundBoardXML.fill(dropdown)
        self.soundBoardXML.bindFillEvents(dropdown)

if __name__ == '__main__':
    wndMain()
    Gtk.main()
