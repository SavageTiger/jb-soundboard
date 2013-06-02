
from xml.dom import minidom

class SoundboardXML:

    dom = None

    def __init__(self, xml):
        self.dom = minidom.parseString(xml)

    def getFilePath(self, id, primary):
        button = self.__getButton(id, primary)

        if button != None:
            binding = button.getElementsByTagName('binding')

            if binding.length > 0:
                return binding[0].childNodes[0].nodeValue

        return ''

    def isBound(self, id, primary):
        button = self.__getButton(id, primary)

        if button != None:
            if int(button.getAttribute('id')) == id:
                return True

        return False

    def __getButton(self, id, primary):
        if primary:
            parentNode = self.dom.getElementsByTagName('primary')
        else:
            parentNode = self.dom.getElementsByTagName('secondary')

        if parentNode.length > 0:
            for button in parentNode[0].getElementsByTagName('button'):
                if int(button.getAttribute('id')) == id:
                    return button
