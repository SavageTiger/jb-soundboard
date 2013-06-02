
import modSoundboardXML
import pyxhook

import gobject # Without the legacy gobject gstreamer will segfault
from gi.repository import Gtk, GObject

import os
import glob
import gst
import threading

class SoundboardInterface:

    player = None

    buttonGrids = []
    buttonHoyKeys = {}
    buttonActive = None
    activeHotKey = ''

    xml = {}
    xmlProperties = None

    def fillDropdown(self, dropdown):
        xmlFiles = glob.glob('./SoundBoards/*.xml')

        for xmlFile in xmlFiles:
            xmlFileContent = open(xmlFile).read()

            xmlFile = xmlFile.replace('./SoundBoards/', '');
            xmlFile = xmlFile.replace('.xml', '');
            xmlFile = xmlFile.capitalize()

            self.xml[xmlFile] = xmlFileContent

            dropdown.append_text(xmlFile)

    def bindDropdownEvents(self, dropdown):
        dropdown.connect("changed", self.initBoard)

    def initBoard(self, dropdown):
        self.xmlProperties = modSoundboardXML.SoundboardXML(
            self.xml[dropdown.get_active_text()]
        )

        for buttonGrid in self.buttonGrids:
            for button in buttonGrid:
                primaryGrid = (button.get_name().find('primary') != -1)

                offset = int(
                    button.get_name()
                    .replace('primary_button_', '')
                    .replace('secondary_button_', '')
                    .replace('_playing', '')
                )

                button.set_sensitive(self.xmlProperties.isBound(offset, primaryGrid))

    def initPlayer(self):
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.__playerMessage)

    def __playerMessage(self, bus, msg):
        t = msg.type

        if t == gst.MESSAGE_EOS: # EOS = End of song
            self.player.set_state(gst.STATE_NULL)
            self.buttonClicked(self.buttonActive)
            self.buttonActive = None

    def startHookManagerThread(self):
        GObject.threads_init()
        gobject.threads_init()
        thr = threading.Thread(target=self.bindHookManager)
        thr.daemon = True
        thr.start()

    def __keyCapture(self, event):
        if event.MessageName == 'key up' and event.Key == self.activeHotKey:
            self.activeHotKey = ''
        elif event.MessageName == 'key down' and self.activeHotKey == '':
            self.activeHotKey = event.Key
        elif event.MessageName == 'key down' and self.activeHotKey != '':
            if str(self.activeHotKey + ' + ' + event.Key) in self.buttonHoyKeys:
                button = self.buttonHoyKeys[self.activeHotKey + ' + ' + event.Key]

                self.buttonClicked(button)

    def bindHookManager(self):
        hm = pyxhook.HookManager()
        hm.HookKeyboard()
        hm.KeyDown = self.__keyCapture
        hm.KeyUp = self.__keyCapture
        hm.run()

    def buttonClicked(self, sender):
        if sender.get_sensitive() == False:
            return

        if self.buttonActive != None and self.buttonActive != sender:
            self.buttonClicked(self.buttonActive)

        offset = int(
            sender.get_name()
            .replace('primary_button_', '')
            .replace('secondary_button_', '')
            .replace('_playing', '')
        )

        filePath = self.xmlProperties.getFilePath(
            offset,
            (sender.get_name().find('primary') != -1)
        )

        if os.path.isfile(filePath):
            if sender.get_name().find('_playing') > 0:
                self.player.set_state(gst.STATE_NULL)

                self.buttonActive = None
                sender.set_name(sender.get_name().replace('_playing', ''))
            else:
                self.player.set_property("uri", "file://" + filePath)
                self.player.set_state(gst.STATE_PLAYING)

                self.buttonActive = sender
                sender.set_name(sender.get_name() + '_playing')

    def renderButtons(self, container, hotkey, primary):
        offset = 0

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        grid.show()

        container.add(grid)
        self.buttonGrids.append(grid)

        for r in range(0, 5):
            for c in range(0, 2):
                offset = offset + 1

                button = Gtk.Button(
                    label = 'Clip ' + str(offset) + '\r\n' +
                    hotkey + ' + '  + str(offset)
                )
                if primary:
                    button.set_name('primary_button_' + str(offset))
                else:
                    button.set_name('secondary_button_' + str(offset))

                button.set_sensitive(False)
                button.set_size_request(120, 80)
                button.show()
                button.connect('pressed', self.buttonClicked)

                self.buttonHoyKeys[hotkey + ' + ' + str(offset)] = button

                grid.attach(button, c, r, 1, 1)
