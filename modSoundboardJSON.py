
import json

class SoundboardJSON:

    jsonBuffer = None

    def __init__(self, jsonString):
        self.jsonBuffer = json.loads(jsonString)

    def getFilePath(self, id, primary):
        return self.__getBinding(id, primary)

    def isBound(self, id, primary):
        return (self.__getBinding(id, primary) != None)

    def __getBinding(self, id, primary):
        buttonId = 'button_' + str(id)

        if primary:
            container = self.jsonBuffer['primary']
        else:
            container = self.jsonBuffer['secondary']

        if buttonId in container:
            if 'binding' in container[buttonId]:
                return container[buttonId]['binding']

        return None
