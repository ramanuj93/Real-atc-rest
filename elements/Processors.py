from enum import Enum


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
    HARRIER = 4,
    HAWG = 5,
    UNKNOWN = 6


class FlightObject:
    def __init__(self, callsign: str, type_air: AIRCRAFT, status: FLIGHT_STATE,
                 size,
                 altitude=None,
                 radial=None,
                 distance=None,
                 runway: str = None):
        self.callsign = callsign
        self.type_air = type_air
        self.status = status
        self.size = size
        self.altitude = altitude
        self.radial = radial
        self.distance = distance
        self.runway: str = runway

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


class HoldShortRunwayCall(CallObject):

    def __init__(self, freq, recipient, caller, runway):
        super().__init__(freq, recipient=recipient, caller=caller,
                         runway=runway, type_call=FLIGHT_STATE.HOLD_SHORT_RUNWAY)


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

    def __init__(self, freq: float, name: str, base_ref):
        self._freq = freq
        self._name = name
        self._base_ref = base_ref
        self._registry = []

    def _add_flight(self, plane):
        self._registry.append(plane)
        return


class TowerController(Controller):

    def receive_transmission(self, call: CallObject):
        if call.freq == self._freq:
            return self.__process_transmission(call)
        return

    def __process_transmission(self, call: CallObject):
        response: ControllerResponseCall = ControllerResponseCall(self._freq, ATC_RESPONSE.STANDBY, caller=self._name)
        flight: FlightObject = self._base_ref.aircraft_map.get(call.caller, None)
        if call.type_call == FLIGHT_STATE.TAKE_RUNWAY:
            if not flight or flight.status != FLIGHT_STATE.HOLD_SHORT_RUNWAY:
                response.deny()
            else:
                if self._base_ref.register_take_active(flight.callsign, flight.runway):
                    flight.status = FLIGHT_STATE.TAKE_RUNWAY
                    response.grant()
                else:
                    response.standby()
        elif call.type_call == FLIGHT_STATE.TAKEOFF:
            if not flight or flight.status != FLIGHT_STATE.TAKE_RUNWAY:
                response.deny()
            else:
                self._base_ref.allow_takeoff(flight.size, flight.runway)
                flight.status = FLIGHT_STATE.TAKEOFF
                response.grant()
                self._base_ref.aircraft_map[call.caller] = flight

        return response


class GroundController(Controller):

    def receive_transmission(self, call: CallObject):
        if call.freq == self._freq:
            return self.__process_transmission(call)
        return

    def __process_transmission(self, call):
        response: ControllerResponseCall = ControllerResponseCall(self._freq, call.type_call, recipient=call.caller, caller=self._name)
        flight: FlightObject = self._base_ref.aircraft_map.get(call.caller, None)
        if call.type_call == FLIGHT_STATE.TAXI:
            if not flight:
                flight = FlightObject(call.caller, call.type_air, FLIGHT_STATE.NEW, call.size)
            runway_assigned = self._base_ref.register_taxi(flight.size)
            if runway_assigned:
                response.runway = runway_assigned
                flight.runway = runway_assigned
                flight.status = FLIGHT_STATE.TAXI
                response.grant()
            else:
                flight.status = FLIGHT_STATE.WAIT_FOR_TAXI
                response.standby()
            self._base_ref.aircraft_map[call.caller] = flight
        elif call.type_call == FLIGHT_STATE.HOLD_SHORT_RUNWAY:
            if not flight or flight.status != FLIGHT_STATE.TAXI:
                response.deny()
            else:
                self._base_ref.register_hold_runway(flight.size, flight.runway)
                flight.status = FLIGHT_STATE.HOLD_SHORT_RUNWAY
                response.acknowledge()
                self._base_ref.aircraft_map[call.caller] = flight

        return response























