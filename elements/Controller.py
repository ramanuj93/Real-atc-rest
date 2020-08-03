import abc
from enum import Enum

from elements.Airport import FlightObject, Airport


class ATC_RESPONSE(Enum):
    GRANTED = 1,
    DENIED = 2,
    STANDBY = 3,
    ACKNOWLEDGE = 4


class FLIGHT_STATE(Enum):
    TAXI = 1,
    HOLD_SHORT_RUNWAY = 2,
    TAKE_RUNWAY = 3,
    TAKEOFF = 4,
    INBOUND = 5,
    INITIAL = 6,
    FINAL = 7,
    CLEAR_RUNWAY = 8,
    DEPART_RUNWAY = 9,
    UNKNOWN = 10,
    NEW = 11,
    WAIT_FOR_TAXI = 12


class AIRCRAFT(Enum):
    HORNET = 1,
    VIPER = 2,
    TOMCAT = 3,
    HARRIER = 4


class CallObject:

    def __init__(self, freq,
                 type_call,
                 caller=None,
                 recipient=None,
                 flight=None,
                 size=None,
                 type_air=None,
                 altitude=None,
                 distance=None,
                 runway=None,
                 radial=None,
                 grant_status=None):
        self.freq = freq
        self.caller = caller
        self.flight = flight
        self.recipient = recipient
        self.flight = flight
        self.size = size
        self.type_air = type_air
        self.type_call = type_call
        self.altitude = altitude
        self.distance = distance
        self.runway = runway
        self.radial = radial
        self.grant_status = grant_status


class ControllerResponseCall(CallObject):

    def grant(self):
        self.grant_status = ATC_RESPONSE.GRANTED

    def standby(self):
        self.grant_status = ATC_RESPONSE.STANDBY

    def deny(self):
        self.grant_status = ATC_RESPONSE.DENIED

    def acknowledge(self):
        self.grant_status = ATC_RESPONSE.ACKNOWLEDGE


class TaxiCall(CallObject):

    def __init__(self, freq, recipient, caller, type_air, size, runway):
        super().__init__(freq, recipient=recipient, caller=caller, type_air=type_air,
                         size=size, runway=runway, type_call=FLIGHT_STATE.TAXI)


class RunwayEnterCall(CallObject):

    def __init__(self, freq, recipient, caller):
        super().__init__(freq, recipient=recipient, caller=caller, type_call=FLIGHT_STATE.TAKE_RUNWAY)


class TakeoffCall(CallObject):

    def __init__(self, freq, recipient, caller):
        super().__init__(freq, recipient=recipient, caller=caller, type_call=FLIGHT_STATE.TAKEOFF)


class DepartCall(CallObject):

    def __init__(self, freq, recipient, caller):
        super().__init__(freq, recipient=recipient, caller=caller, type_call=FLIGHT_STATE.DEPART_RUNWAY)


class InboundCall(CallObject):

    def __init__(self, freq, recipient, caller, type_air, size, altitude, radial, distance):
        super().__init__(freq, recipient=recipient, caller=caller, type_air=type_air, distance=distance,
                         size=size, altitude=altitude, radial=radial, type_call=FLIGHT_STATE.INBOUND)


class Controller:

    def __init__(self, freq: float, name: str, base_ref: Airport):
        self._freq = freq
        self._name = name
        self._base_ref = base_ref
        self._registry = []
        self._aircraft_map: {[str]: FlightObject} = {}

    def _add_flight(self, plane):
        self._registry.append(plane)
        return

    @abc.abstractmethod
    def __process_transmission(self, call: CallObject):
        return

    def __receive_transmission(self, call: CallObject):
        if call.freq == self._freq:
            self.__process_transmission(call)
        return


class TowerController(Controller):
    def __process_transmission(self, call: CallObject):
        if call.type_call == FLIGHT_STATE.TAXI:
            return


class GroundController(Controller):

    def __process_transmission(self, call):
        response: ControllerResponseCall = ControllerResponseCall(freq=self._freq)
        flight: FlightObject = self._aircraft_map.get(call.caller, None)
        if call.type_call == FLIGHT_STATE.TAXI:
            if not flight:
                flight = FlightObject(call.caller, call.type_air, FLIGHT_STATE.NEW, call.size)
            runway_assigned = self._base_ref.register_taxi(flight.callsign)
            if runway_assigned:
                response.runway = runway_assigned
                flight.runway = runway_assigned
                flight.status = FLIGHT_STATE.TAXI
                response.grant()
            else:
                flight.status = FLIGHT_STATE.WAIT_FOR_TAXI
                response.standby()
            self._aircraft_map[call.caller] = flight
        elif call.type_call == FLIGHT_STATE.HOLD_SHORT_RUNWAY:
            if not flight or flight.status != FLIGHT_STATE.TAXI:
                response.deny()
            else:
                self._base_ref.register_take_active(flight.callsign)
                flight.status = FLIGHT_STATE.HOLD_SHORT_RUNWAY
                response.acknowledge()
        elif call.type_call == FLIGHT_STATE.TAKE_RUNWAY:
            if not flight or flight.status != FLIGHT_STATE.HOLD_SHORT_RUNWAY:
                response.deny()
            else:
                self._base_ref.register_take_active(flight.callsign)
                flight.status = FLIGHT_STATE.TAKE_RUNWAY
                response.grant()


        return response























