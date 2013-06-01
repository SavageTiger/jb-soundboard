
import glob

class SoundboardXML:

    xml = {}

    def fill(self, dropdown):
        xmlFiles = glob.glob('./SoundBoards/*.xml')

        for xmlFile in xmlFiles:
            xmlFileContent = open(xmlFile).read()

            xmlFile = xmlFile.replace('./SoundBoards/', '');
            xmlFile = xmlFile.replace('.xml', '');
            xmlFile = xmlFile.capitalize()

            self.xml[xmlFile] = xmlFileContent

            dropdown.append_text(xmlFile)

    def bindFillEvents(self, dropdown):
        dropdown.connect("changed", self.initBoard)

    def initBoard(self, dropdown):
        print self.xml[dropdown.get_active_text()]
