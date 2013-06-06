#!/usr/bin/env python

import sys, os

from gi.repository import Gtk, Gdk

import modSoundboardInterface

class wndMain:

    SoundboardInterface = None

    def __init__(self):
        # Render the main window
        self.glade = Gtk.Builder()
        self.glade.add_from_file('GUI.glade')

        window = self.glade.get_object('wndMain')
        window.set_title('SoundBoard 1.0 [JB Edition]')
        window.show_all()
        window.connect('delete-event', Gtk.main_quit)
        window.set_name('wndMain')

        # Add a awesome gtk3 style-provider
        styleProvider = Gtk.CssProvider()
        styleProvider.load_from_data(open('./Skin/skin.css').read())

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            styleProvider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Fill the soundboards dropdpown and bind events
        dropdown = self.glade.get_object('cmbSoundboard')

        self.soundBoardInterface = modSoundboardInterface.SoundboardInterface()
        self.soundBoardInterface.fillDropdown(dropdown)
        self.soundBoardInterface.bindDropdownEvents(dropdown)

        # Set state to ready
        self.soundBoardInterface.setState(
            0, 0,
            [self.glade.get_object('playState'), self.glade.get_object('progressState')]
        )

        # Render the soundboard buttons
        primaryContainer = self.glade.get_object('frmPrimary')
        secondaryContainer = self.glade.get_object('frmSecondary')

        self.soundBoardInterface.renderButtons(primaryContainer, 'Control_L', True);
        self.soundBoardInterface.renderButtons(secondaryContainer, 'Alt_L', False);

        # Yeah...there is a keylogger in this software package
        # They can actually be usefull you know
        self.soundBoardInterface.startHookManagerThread();

        # Initialize the gstreamer player
        self.soundBoardInterface.initPlayer()

if __name__ == '__main__':
    wndMain()
    Gtk.main()
