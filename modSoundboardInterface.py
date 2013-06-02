
import modSoundboardXML
import pyxhook

from gi.repository import Gtk
import os
import glob
import gst

class SoundboardInterface:

    player = None
    buttonGrids = []
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
                )

                button.set_sensitive(self.xmlProperties.isBound(offset, primaryGrid))

    def initPlayer(self):
		self.player = gst.element_factory_make("playbin2", "player")
		fakesink = gst.element_factory_make("fakesink", "fakesink")
		self.player.set_property("video-sink", fakesink)

    def bindHookManager(self):
        hm = pyxhook.HookManager()
        hm.HookKeyboard()
        hm.KeyDown = hm.printevent
        hm.run()

    def buttonClicked(self, sender):
        offset = int(
            sender.get_name()
            .replace('primary_button_', '')
            .replace('secondary_button_', '')
        )

        filePath = self.xmlProperties.getFilePath(
            offset,
            (sender.get_name().find('primary') != -1)
        )

        if os.path.isfile(filePath):
            self.player.set_property("uri", "file://" + filePath)
            self.player.set_state(gst.STATE_PLAYING)

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
                button.set_size_request(80, 80)
                button.show()
                button.connect('pressed', self.buttonClicked)

                grid.attach(button, c, r, 1, 1)
