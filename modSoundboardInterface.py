
from gi.repository import Gtk
import glob

class SoundboardInterface:

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
        print self.xml[dropdown.get_active_text()]

    def renderButtons(self, container, hotkey):
        offset = 0

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)


        container.add(grid)
        grid.show()

        for r in range(0, 5):
            for c in range(0, 2):
                offset = offset + 1

                button = Gtk.Button(
                    label = 'Clip ' + str(offset) + '\r\n' +
                    hotkey + ' + '  + str(offset)
                )
                button.set_size_request(80, 80)
                button.show()

                grid.attach(button, c, r, 1, 1)
