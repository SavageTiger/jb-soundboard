#!/usr/bin/env python

import sys, os

from gi.repository import Gtk

class wndMain:
    def __init__(self):
        self.glade = Gtk.Builder()
        self.glade.add_from_file("GUI.glade")
        .show_all()
        self.glade.get_object("wndMain").connect("delete-event", Gtk.main_quit)

if __name__ == '__main__':
	wndMain()
	Gtk.main()
