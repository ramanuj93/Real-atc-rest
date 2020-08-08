from elements.Processors import GroundController, TowerController


class Runway:

    def __init__(self, ident: str, hold_size: int):
        self.id: str = ident
        self._hold_size: int = hold_size
        self._hold_short = 0
        self.taxi_to = 0
        self._on_runway = 0
        self._incoming = 0
        self._departing = 0
        self._on_final = 0

    def add_flight_taxi(self, flights) -> (bool, bool):
        if (self._hold_short + self.taxi_to + flights) <= (self._hold_size + 4):
            is_clean = False
            if (self._hold_short + self.taxi_to + self._on_runway + self._incoming) == 0:
                is_clean = True
            self.taxi_to += flights
            return True, is_clean
        return False, False

    def remove_flight_taxi(self, flights):
        if self.taxi_to > 0:
            self.taxi_to -= flights
            return True
        return False

    def add_flight_active(self, flights):
        if self._on_runway == 0 and self._departing == 0 and self._on_final == 0:
            self._on_runway += flights
            return True
        return False

    def add_flight_hold_short(self, flights):
        if self._hold_short < self._hold_size:
            self._hold_short += flights
            return True
        return False

    def remove_flight_hold_short(self, flights):
        if self._hold_short >= flights:
            self._hold_short -= flights
            return True
        return False

    def clear_takeoff(self, flights):
        if self._on_runway >= flights and self._departing:
            self._on_runway -= flights
            self._departing += flights
            return True
        return False

    def clear_airspace(self, flights):
        if self._departing >= flights:
            self._departing -= flights
            return True
        return False

    def add_flight_incoming(self, flight):
        self._incoming += flight


class Airport:

    def __init__(self, name, runways_map: {}):
        self._runways_map: {} = runways_map
        self.aircraft_map: {} = {}
        self._ground: GroundController = GroundController(104, name + ' Traffic', self)
        self._tower: TowerController = TowerController(105, name + ' Tower', self)

    def activate(self):
        self._ground.start()
        self._tower.start()

    def close(self):
        self._ground.close()
        self._tower.close()

    # def receive_transmission(self, call: CallObject):
    #     if call:
    #         if call.type_call in [FLIGHT_STATE.TAXI, FLIGHT_STATE.HOLD_SHORT_RUNWAY]:
    #             response = self._ground.receive_transmission(call)
    #             return response

    def register_taxi(self, flights: float):
        for runway in self._runways_map.keys():
            runway_assigned, runway_clean = self._runways_map[runway].add_flight_taxi(flights)
            if runway_assigned:
                return runway, runway_clean
        return None, False

    def register_hold_runway(self, flights, runway):
        if self._runways_map[runway].add_flight_hold_short(flights):
            return self._runways_map[runway].remove_flight_taxi(flights)
        return False

    def register_take_active(self, flights, runway, is_direct=False):
        if self._runways_map[runway].add_flight_active(flights):
            if is_direct:
                self._runways_map[runway].remove_flight_taxi(flights)
            else:
                self._runways_map[runway].remove_flight_hold_short(flights)

    def allow_takeoff(self, flights, runway):
        return self._runways_map[runway].clear_takeoff(flights)

    def clear_airspace(self, flights, runway):
        self._runways_map[runway].clear_airspace(flights)

    def call_hold_short(self, flight, runway):
        return

    def call_departure(self, flight, runway):
        return

    def request_inbound(self, flight, size, bearing, distance, altitude):
        return

