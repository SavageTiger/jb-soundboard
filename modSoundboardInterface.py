
import modSoundboardXML
import modSoundboardJSON
import pyxhook

import gobject # Without the legacy gobject gstreamer will segfault
from gi.repository import Gtk, GObject

import os
import glob
import gst
import threading

class SoundboardInterface:

    player = None
    playerDuration = 0

    volumePrimary = None
    volumeSecondary = None

    buttonGrids = []
    buttonHoyKeys = {}
    buttonActive = None
    activeHotKey = ''

    stateObjects = None
    stateId = 0

    xml = {}
    json = {}
    ioProperties = None

    def setState(self, progress, total = 0, stateObjects = None):
        if stateObjects != None:
            self.stateId = stateObjects[0].get_context_id('SB')
            self.stateObjects = stateObjects

        if progress <= 0:
            self.stateObjects[0].push(self.stateId, 'Ready')
        else:
            fraction = (progress * 1e2 / total) / 100

            self.stateObjects[0].push(self.stateId, 'Playing [' + str(progress) + 'ms]')
            self.stateObjects[1].set_fraction(fraction)

    def startStateThread(self, totalDuration = 0):
        if self.playerDuration <= 0:
            self.setState(0)
        else:
            self.setState(self.playerDuration, totalDuration)

            self.playerDuration = self.playerDuration - 100

            threading.Timer(0.1, self.startStateThread, (totalDuration, )).start()

    def fillDropdown(self, dropdown):
        configFiles = glob.glob('./SoundBoards/*.xml')
        configFiles = configFiles + glob.glob('./SoundBoards/*.json')

        for configFile in configFiles:
            isXml = (configFile.find('.xml') > 0)
            fileContent = open(configFile).read()

            configFile = configFile.replace('./SoundBoards/', '');
            configFile = configFile.replace('.xml', '').replace('.json', '');
            configFile = configFile.capitalize()

            if isXml:
                self.xml[configFile] = fileContent
            else:
                self.json[configFile] = fileContent

            dropdown.append_text(configFile)

    def bindDropdownEvents(self, dropdown):
        dropdown.connect("changed", self.initBoard)

    def initBoard(self, dropdown):
        if dropdown.get_active_text() in self.xml:
            self.ioProperties = modSoundboardXML.SoundboardXML(
                self.xml[dropdown.get_active_text()]
            )
        elif dropdown.get_active_text() in self.json:
            self.ioProperties = modSoundboardJSON.SoundboardJSON(
                self.json[dropdown.get_active_text()]
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

                if self.ioProperties.isBound(offset, primaryGrid):
                    filePath = self.ioProperties.getFilePath(offset, primaryGrid)
                    filePath = os.path.basename(filePath)

                    buttonCaption = button.get_label().split('\r\n')
                    buttonCaption = filePath + '\r\n' + buttonCaption[1]

                    button.set_sensitive(True)
                else:
                    buttonCaption = button.get_label().split('\r\n')
                    buttonCaption = 'Clip ' + str(offset) + '\r\n' + buttonCaption[1]

                    button.set_sensitive(False)

                button.set_label(buttonCaption)

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
        elif t == gst.MESSAGE_DURATION:
            duration = msg.parse_duration()[1]
            duration = duration / 1000000 # Convert to ms

            if self.playerDuration <= 0:
                self.playerDuration = duration
                self.startStateThread(self.playerDuration)
            else:
                self.playerDuration = duration

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

        filePath = self.ioProperties.getFilePath(
            offset,
            (sender.get_name().find('primary') != -1)
        )

        if os.path.isfile(filePath):
            filePath = os.path.abspath(filePath)

            if sender.get_name().find('_playing') > 0:
                self.player.set_state(gst.STATE_NULL)

                self.buttonActive = None
                sender.set_name(sender.get_name().replace('_playing', ''))
            else:
                self.player.set_property("uri", "file://" + filePath)
                self.player.set_state(gst.STATE_PLAYING)

                if sender.get_name().find('primary') == 0:
                    self.player.set_property("volume", (self.volumePrimary.get_value() / 100))
                else:
                    self.player.set_property("volume", (self.volumeSecondary.get_value() / 100))

                self.buttonActive = sender
                sender.set_name(sender.get_name() + '_playing')

    def bindVolumeEvents(self, volumePrimary, volumeSecondary):
        self.volumePrimary = volumePrimary
        self.volumeSecondary = volumeSecondary

        volumePrimary.set_name('volumePrimary')
        volumeSecondary.set_name('volumeSecondary')

        adjumentPrimary = Gtk.Adjustment(100, 0, 100, 5, 10, 0)
        adjumentSecondary = Gtk.Adjustment(100, 0, 100, 5, 10, 0)

        volumePrimary.set_adjustment(adjumentPrimary)
        volumeSecondary.set_adjustment(adjumentSecondary)

        volumePrimary.set_size_request(0, 30)
        volumeSecondary.set_size_request(0, 30)

        volumePrimary.connect('value-changed', self.volumeChanged)
        volumeSecondary.connect('value-changed', self.volumeChanged)

    def volumeChanged(self, sender):
        if self.buttonActive == None:
            return
        elif sender.get_name() == 'volumePrimary' and self.buttonActive.get_name().find('primary') == -1:
            return
        elif sender.get_name() == 'volumeSecondary' and self.buttonActive.get_name().find('secondary') == -1:
            return

        self.player.set_property("volume", (sender.get_value() / 100))

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
                    hotkey + ' + '  + str(offset).replace('10', '0')
                )
                if primary:
                    button.set_name('primary_button_' + str(offset))
                else:
                    button.set_name('secondary_button_' + str(offset))

                button.set_sensitive(False)
                button.set_size_request(120, 80)
                button.show()
                button.connect('pressed', self.buttonClicked)

                self.buttonHoyKeys[hotkey + ' + ' + str(offset).replace('10', '0')] = button

                grid.attach(button, c, r, 1, 1)
