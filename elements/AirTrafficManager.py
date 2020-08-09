from constants.HelperEntity import ControllerResponseCall
from elements.Entities import Airport
import threading
import time
from elements.RadioEngine import EmissionsControl
from elements.TextEngine import TextEngine


class ResponseReader(threading.Thread):
    def __init__(self, speaker_obj):
        threading.Thread.__init__(self)
        self._exit: bool = False
        self._synthesizer = speaker_obj

    def close(self):
        self._exit = True

    def run(self):
        while not self._exit:
            time.sleep(1)
            responses: [ControllerResponseCall] = EmissionsControl.broadcast_response()
            if responses:
                for response in responses:
                    text = TextEngine.CallToText(response)
                    print(text)
                    self._synthesizer.synthesise(text)
                    self._synthesizer.speak()


class AirTrafficManager:

    def __init__(self, airports: [Airport], speaker_obj):
        self._airports: [Airport] = airports
        self._reader = ResponseReader(speaker_obj)

    def begin(self):
        self._reader.start()
        for airport in self._airports:
            airport.activate()

    def shut_down(self):
        self._reader.close()
        for airport in self._airports:
            airport.close()


