jb-soundboard
=============
Soundboard application written in Python for Linux

Description
=========
jb-soundboard is an application designed to play sound clips from
preconfigured XML or JSON files (soundboards).

Features
=========
- Create multiple soundboard configurations in XML or JSON
- 20 clips per soundboard configurable
- Play and stop clips using Hotkeys (also without focus on the application)
- Supports all the multimedia types that gStreamer is capable of playing

Requirements
============
- Gtk3
- Pyhon version 2.x (not 3!), tested and developed on 2.7.4
- gstreamer0.10-python (may be named python-gst0.10)
- pygtk (or python-glade2) (gui)
- python2-xlib (hotkey capture)
- python2-imaging
