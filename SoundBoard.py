#!/usr/bin/env python

import sys, os

from gi.repository import Gtk

import modSoundboardInterface

class wndMain:

    SoundboardInterface = None

    def __init__(self):
        # Render the main window
        self.glade = Gtk.Builder()
        self.glade.add_from_file("GUI.glade")
        self.glade.get_object("wndMain").show_all()
        self.glade.get_object("wndMain").connect("delete-event", Gtk.main_quit)

        # Fill the soundboards dropdpown and bind events
        dropdown = self.glade.get_object("cmbSoundboard")

        self.soundBoardInterface = modSoundboardInterface.SoundboardInterface()
        self.soundBoardInterface.fillDropdown(dropdown)
        self.soundBoardInterface.bindDropdownEvents(dropdown)

        # Render the soundboard buttons
        primaryContainer = self.glade.get_object("frmPrimary")
        secondaryContainer = self.glade.get_object("frmSecondary")

        self.soundBoardInterface.renderButtons(primaryContainer, 'Control_L', True);
        self.soundBoardInterface.renderButtons(secondaryContainer, 'Alt_L', False);

        # Initialize the gstreamer player
        self.soundBoardInterface.initPlayer()

        # Yeah...there is a keylogger in this software package
        # They can actually be usefull you know
        self.soundBoardInterface.startHookManagerThread();

if __name__ == '__main__':
    wndMain()
    Gtk.main()
