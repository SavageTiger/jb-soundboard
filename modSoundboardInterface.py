
import modSoundboardXML
from gi.repository import Gtk
import glob

class SoundboardInterface:

    buttonGrids = []
    xml = {}

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
        offset = 0

        xmlProperties = modSoundboardXML.SoundboardXML(
            self.xml[dropdown.get_active_text()]
        )

        for buttonGrid in self.buttonGrids:
            for button in buttonGrid:
                offset = offset + 1

                button.set_sensitive(xmlProperties.isBound(offset))



    def renderButtons(self, container, hotkey):
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
                button.set_sensitive(False)
                button.set_size_request(80, 80)
                button.show()

                grid.attach(button, c, r, 1, 1)
