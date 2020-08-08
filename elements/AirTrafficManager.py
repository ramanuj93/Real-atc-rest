from elements.Entities import Airport


class AirTrafficManager:

    def __init__(self, airports: [Airport]):
        self._airports: [Airport] = airports

    def begin(self):
        for airport in self._airports:
            airport.activate()

    def shut_down(self):
        for airport in self._airports:
            airport.close()


