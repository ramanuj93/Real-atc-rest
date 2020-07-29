from elements.Controller import GroundController, TowerController


class Runway:

    def __init__(self):
        self._hold_short = []
        self._active = []
        self._incoming = []

    def add_flight_taxi(self, flight):
        self._hold_short.append(flight)

    def add_flight_active(self, flight):
        self._active.append(flight)

    def clear_takeoff(self, flight):
        self._active.append(flight)

    def add_flight_incoming(self, flight):
        self._incoming.append(flight)


class Airport:

    def __init__(self, name, runways_map):
        self._runways_map = runways_map
        self._ground = GroundController(name + '_ground', self, runways_map)
        self._tower = TowerController(name + '_tower', self, runways_map)

    def register_taxi(self, flight, runway):
        self._runways_map[runway].add_flight_taxi(flight)

    def register_hold_runway(self, flight, runway):
        self._runways_map[runway].add_flight_active(flight)

    def allow_takeoff(self, flight, runway):
        self._runways_map[runway].clear_takeoff(flight)

    def request_taxi(self, flight, size, runway):
        return

    def call_hold_short(self, flight, runway):
        return

    def call_take_active(self, flight, runway):
        return

    def call_departure(self, flight, runway):
        return

    def request_inbound(self, flight, size, bearing, distance, altitude):
        return

