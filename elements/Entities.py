from elements.Processors import GroundController, TowerController, FLIGHT_STATE, CallObject


class Runway:

    def __init__(self, ident, hold_size):
        self.id = ident,
        self._hold_size = hold_size
        self._hold_short = 0
        self.taxi_to = 0
        self._on_runway = 0
        self._incoming = 0

    def add_flight_taxi(self, flights):
        if (self._hold_short + self.taxi_to + flights) <= (self._hold_size + 4):
            self.taxi_to += flights
            return True
        return False

    def remove_flight_taxi(self, flights):
        if self.taxi_to > 0:
            self.taxi_to -= flights
            return True
        return False

    def add_flight_active(self, flights):
        if self._on_runway == 0:
            self._on_runway += flights
            return True
        return False

    def add_flight_hold_short(self, flights):
        if self._hold_short < self._hold_size:
            self._hold_short += flights
            return True
        return False

    def clear_takeoff(self, flight):
        self._on_runway -= flight

    def add_flight_incoming(self, flight):
        self._incoming += flight


class Airport:

    def __init__(self, name, runways_map: {}):
        self._runways_map: {} = runways_map
        self.aircraft_map: {} = {}
        self._ground: GroundController = GroundController(104, name + ' Traffic', self)
        self._tower: TowerController = TowerController(105, name + ' Tower', self)

    def receive_transmission(self, call: CallObject):
        if call:
            if call.type_call in [FLIGHT_STATE.TAXI, FLIGHT_STATE.HOLD_SHORT_RUNWAY]:
                response = self._ground.receive_transmission(call)
                return response

    def register_taxi(self, flight: float):
        for runway in self._runways_map.keys():
            if self._runways_map[runway].add_flight_taxi(flight):
                return runway
        return None

    def register_hold_runway(self, flight, runway):
        if self._runways_map[runway].add_flight_hold_short(flight):
            return self._runways_map[runway].remove_flight_taxi(flight)
        return False

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

