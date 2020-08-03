from elements.Controller import GroundController, TowerController, AIRCRAFT, FLIGHT_STATE


class FlightObject:
    def __init__(self, callsign: str, type_air: AIRCRAFT, status: FLIGHT_STATE,
                 size,
                 altitude=None,
                 radial=None,
                 distance=None,
                 runway=None):
        self.callsign = callsign,
        self.type_air = type_air,
        self.status = status,
        self.size = size,
        self.altitude = altitude,
        self.radial = radial,
        self.distance = distance,
        self.runway = runway


class Runway:

    def __init__(self, hold_size):
        self._hold_size = hold_size
        self._hold_short = []
        self._active = []
        self._incoming = []

    def add_flight_taxi(self, flight):
        if len(self._hold_short) < self._hold_size:
            self._hold_short.append(flight)
            return True
        return False

    def add_flight_active(self, flight):
        if len(self._active) == 0:
            self._active.append(flight)
            return True
        return False

    def clear_takeoff(self, flight):
        self._active.append(flight)

    def add_flight_incoming(self, flight):
        self._incoming.append(flight)


class Airport:

    def __init__(self, name, runways_map: {[str]: FlightObject}):
        self._runways_map: {[str]: FlightObject} = runways_map
        self._ground = GroundController(104, name + '_ground', self)
        self._tower = TowerController(105, name + '_tower', self)

    def register_taxi(self, flight: FlightObject):
        for runway in self._runways_map.keys():
            if self._runways_map[runway].add_flight_taxi(flight):
                return runway
        return None

    def register_hold_runway(self, flight, runway):
        return self._runways_map[runway].add_flight_active(flight)

    def register_take_active(self, flight, runway):
        return self._runways_map[runway].add_flight_active(flight)

    def allow_takeoff(self, flight, runway):
        self._runways_map[runway].clear_takeoff(flight)

    def request_taxi(self, flight, size, runway):
        return

    def call_hold_short(self, flight, runway):
        return

    def call_departure(self, flight, runway):
        return

    def request_inbound(self, flight, size, bearing, distance, altitude):
        return

