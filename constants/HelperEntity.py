from constants.EnumATC import AIRCRAFT, FLIGHT_STATE, ATC_RESPONSE
import time


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
        self.last_response = None
        self.last_call = None


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
                 grant_status: ATC_RESPONSE = ATC_RESPONSE.RAW,
                 forward_freq=None,
                 request=None):
        self._timestamp = time.time()
        self.freq = freq
        self.caller = caller
        self.flight: FlightObject = flight
        self.recipient = recipient
        self.size = size
        self.type_air = type_air
        self.type_call = type_call
        self.altitude = altitude
        self.distance = distance
        self.runway = runway
        self.radial = radial
        self.grant_status = grant_status
        self.request = request
        self.forward_freq = forward_freq
        self._is_call_valid: bool = False
        self.missing_items = []

    def get_age(self):
        return time.time() - self._timestamp

    def is_valid(self):
        return self._is_call_valid


class TaxiCall(CallObject):

    def __init__(self, freq, recipient, caller, type_air, size, runway):
        super().__init__(freq, recipient=recipient, caller=caller, type_air=type_air,
                         size=size, runway=runway, type_call=FLIGHT_STATE.TAXI)

        if caller and 5 > size > 0:
            self._is_call_valid = True
        else:
            if not caller:
                self.missing_items.append('Callsign')
            if size < 1:
                self.missing_items.append('Flight Size')


class HoldShortRunwayCall(CallObject):

    def __init__(self, freq, recipient, caller, runway):
        super().__init__(freq, recipient=recipient, caller=caller,
                         runway=runway, type_call=FLIGHT_STATE.HOLD_SHORT_RUNWAY)

        if caller and runway:
            self._is_call_valid = True
        else:
            if not caller:
                self.missing_items.append('Callsign')
            if not runway:
                self.missing_items.append('Runway')


class RunwayEnterCall(CallObject):

    def __init__(self, freq, recipient, caller):
        super().__init__(freq, recipient=recipient, caller=caller, type_call=FLIGHT_STATE.TAKE_RUNWAY)
        if caller:
            self._is_call_valid = True
        else:
            self.missing_items.append('Callsign')


class ClearanceCall(CallObject):
    def __init__(self, freq):
        super().__init__(freq, type_call=FLIGHT_STATE.WAIT_CLEARANCE)


class TakeoffCall(CallObject):

    def __init__(self, freq, recipient, caller):
        super().__init__(freq, recipient=recipient, caller=caller, type_call=FLIGHT_STATE.TAKEOFF)


class DepartCall(CallObject):

    def __init__(self, freq, recipient, caller):
        super().__init__(freq, recipient=recipient, caller=caller, type_call=FLIGHT_STATE.DEPART_RUNWAY)

        if caller:
            self._is_call_valid = True
        else:
            if not caller:
                self.missing_items.append('Callsign')


class InboundCall(CallObject):

    def __init__(self, freq, recipient, caller, type_air, size, altitude, radial, distance):
        super().__init__(freq, recipient=recipient, caller=caller, type_air=type_air, distance=distance,
                         size=size, altitude=altitude, radial=radial, type_call=FLIGHT_STATE.INBOUND)


class PartialCall(CallObject):

    def __init__(self, freq, *kwargs, request: CallObject):
        super().__init__(freq, *kwargs)


class ControllerResponseCall(CallObject):

    def __call_complete(self, request, flight, verdict: ATC_RESPONSE):
        self.request = request
        self.request.flight = flight
        self.grant_status = verdict
        self.flight = flight
        self.flight.last_response = self
        self.flight.last_call = request
        if self.type_call == FLIGHT_STATE.UNKNOWN:
            self.type_call = request.type_call

    def grant(self, request, flight):
        self.__call_complete(request, flight, ATC_RESPONSE.GRANTED)

    def standby(self, request, flight):
        self.__call_complete(request, flight, ATC_RESPONSE.STANDBY)

    def deny(self, request, flight):
        self.__call_complete(request, flight, ATC_RESPONSE.DENIED)

    def acknowledge(self, request, flight):
        self.__call_complete(request, flight, ATC_RESPONSE.ACKNOWLEDGE)

    def clarify(self, request):
        self.request = request
        self.grant_status = ATC_RESPONSE.UNCLEAR

    def add_forward_freq(self, freq):
        self.forward_freq = freq
