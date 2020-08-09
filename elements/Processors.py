import threading
import time
from constants.EnumATC import FLIGHT_STATE, ATC_RESPONSE
from constants.HelperEntity import ControllerResponseCall, CallObject, FlightObject, ClearanceCall
from elements.RadioEngine import RadioEngine


class Controller(threading.Thread):

    def __init__(self, freq: float, name: str, base_ref):
        threading.Thread.__init__(self)
        self._radio = RadioEngine(freq)
        self._name = name
        self._base_ref = base_ref
        self._registry = []
        self._poll_interval: float = 0.5
        self._exit: bool = False

    def _resolve_unknown_call(self, call):
        return ControllerResponseCall(self._radio.get_frequency(), ATC_RESPONSE.UNCLEAR)

    def close(self):
        self._exit = True


class TowerController(Controller):

    def receive_transmission(self):
        new_call = self._radio.listen()
        if new_call:
            if new_call.type_call in [FLIGHT_STATE.TAXI_HOLD, FLIGHT_STATE.TAKE_RUNWAY, FLIGHT_STATE.TAKEOFF,
                                      FLIGHT_STATE.DEPART_RUNWAY]:
                if new_call.is_valid():
                    response = self.__process_transmission(new_call)
                    if response:
                        self._radio.respond(response)
                else:
                    response = ControllerResponseCall(new_call.freq, type_call=new_call.type_call)
                    response.clarify(new_call)
        else:
            time.sleep(self._poll_interval)

    def __process_transmission(self, call: CallObject):
        response: ControllerResponseCall = ControllerResponseCall(self._radio.get_frequency(),
                                                                  FLIGHT_STATE.UNKNOWN, caller=self._name,
                                                                  recipient=call.caller)
        flight: FlightObject = self._base_ref.aircraft_map.get(call.caller, None)

        if flight and flight.last_call.type_call == FLIGHT_STATE.WAIT_CLEARANCE:
            return None

        if call.type_call == FLIGHT_STATE.HOLD_SHORT_RUNWAY:
            if not flight or flight.status == FLIGHT_STATE.HOLD_SHORT_RUNWAY:
                response.deny(call, flight)
            else:
                if self._base_ref.register_take_active(flight.size, flight.runway):
                    flight.status = FLIGHT_STATE.TAKE_RUNWAY
                    response.acknowledge(call, flight)
                else:
                    response.standby(call, flight)
        elif call.type_call == FLIGHT_STATE.TAKE_RUNWAY:
            if not flight or not (flight.status == FLIGHT_STATE.HOLD_SHORT_RUNWAY
                                  or flight.status == FLIGHT_STATE.TAKE_RUNWAY):
                response.deny(call, flight)
            else:
                flight.status = FLIGHT_STATE.TAKEOFF
                response.type_call = FLIGHT_STATE.TAKEOFF
                if self._base_ref.allow_takeoff(flight.size, flight.runway):
                    response.acknowledge(call, flight)
                else:
                    response.standby(call, flight)
        elif call.type_call == FLIGHT_STATE.TAKEOFF:
            if not flight or flight.status != FLIGHT_STATE.TAKE_RUNWAY:
                response.deny(call, flight)
            else:
                if self._base_ref.allow_takeoff(flight.size, flight.runway):
                    flight.status = FLIGHT_STATE.TAKEOFF
                    response.acknowledge(call, flight)
                else:
                    response.standby(call, flight)
                self._base_ref.aircraft_map[call.caller] = flight
        elif call.type_call == FLIGHT_STATE.DEPART_RUNWAY:
            if not flight or flight.status != FLIGHT_STATE.TAKEOFF:
                response.deny(call, flight)
            else:
                self._base_ref.clear_airspace(flight.size, flight.runway)
                flight.status = FLIGHT_STATE.DEPART_RUNWAY
                response.acknowledge(call, flight)
                self._base_ref.aircraft_map[call.caller] = flight

        return response

    def process_flight_queue(self):
        for _, flight in self._base_ref.aircraft_map.items():
            if not flight or flight.last_call.freq != self._radio.get_frequency():
                return
            if flight.status == FLIGHT_STATE.TAKE_RUNWAY:
                if self._base_ref.allow_takeoff(flight.size, flight.runway):
                    flight.status = FLIGHT_STATE.TAKEOFF
                    response: ControllerResponseCall = ControllerResponseCall(self._radio.get_frequency(),
                                                                              FLIGHT_STATE.TAKEOFF,
                                                                              caller=self._name)
                    response.grant(ClearanceCall(self._radio.get_frequency()), flight)
                    self._radio.respond(response)
                    time.sleep(0.5)

    def run(self) -> None:
        print('started ' + self._name + ' on freq: ' + str(self._radio.get_frequency()))
        self._radio.start()
        while not self._exit:
            self.receive_transmission()
            self.process_flight_queue()
        print('end tower...')


class GroundController(Controller):

    def receive_transmission(self):
        new_call = self._radio.listen()
        if new_call:
            if new_call.type_call in [FLIGHT_STATE.TAXI, FLIGHT_STATE.HOLD_SHORT_RUNWAY, FLIGHT_STATE.TAKE_RUNWAY]:
                if new_call.is_valid():
                    response = self.__process_transmission(new_call)
                else:
                    response = ControllerResponseCall(new_call.freq, type_call=new_call.type_call)
                    response.clarify(new_call)
                self._radio.respond(response)
        else:
            time.sleep(self._poll_interval)

    def __process_transmission(self, call):
        response: ControllerResponseCall = ControllerResponseCall(self._radio.get_frequency(), call.type_call,
                                                                  recipient=call.caller, caller=self._name)
        flight: FlightObject = self._base_ref.aircraft_map.get(call.caller, None)
        if call.type_call == FLIGHT_STATE.TAXI:
            if not flight:
                flight = FlightObject(call.caller, call.type_air, FLIGHT_STATE.NEW, call.size)
            runway_assigned, is_clean = self._base_ref.register_taxi(flight.size)
            if runway_assigned:
                response.runway = runway_assigned
                flight.runway = runway_assigned
                if is_clean:
                    flight.status = FLIGHT_STATE.TAXI
                else:
                    flight.status = FLIGHT_STATE.TAXI_HOLD
                    response.type_call = FLIGHT_STATE.TAXI_HOLD
                response.grant(call, flight)
            else:
                flight.status = FLIGHT_STATE.WAIT_FOR_TAXI
                response.standby(call, flight)
            self._base_ref.aircraft_map[call.caller] = flight
        elif call.type_call == FLIGHT_STATE.HOLD_SHORT_RUNWAY:
            if not flight or not (flight.status == FLIGHT_STATE.TAXI or flight.status == FLIGHT_STATE.TAXI_HOLD):
                response.deny(call, flight)
            else:
                self._base_ref.register_hold_runway(flight.size, flight.runway)
                flight.status = FLIGHT_STATE.HOLD_SHORT_RUNWAY
                response.forward_freq = 105
                response.acknowledge(call, flight)
                self._base_ref.aircraft_map[call.caller] = flight
        elif call.type_call == FLIGHT_STATE.TAKE_RUNWAY:
            if not flight or not (
                    flight.status == FLIGHT_STATE.TAXI or flight.status == FLIGHT_STATE.HOLD_SHORT_RUNWAY):
                response.deny(call, flight)
            else:
                self._base_ref.register_take_active(flight.size, flight.runway, True)
                flight.status = FLIGHT_STATE.TAKE_RUNWAY
                response.forward_freq = 105
                response.acknowledge(call, flight)
                self._base_ref.aircraft_map[call.caller] = flight

        return response

    def process_flight_queue(self):
        for _, flight in self._base_ref.aircraft_map.items():
            if not flight or flight.last_call.freq != self._radio.get_frequency():
                return
            if flight.status == FLIGHT_STATE.WAIT_FOR_TAXI:
                runway_assigned, is_clean = self._base_ref.register_taxi(flight.size)
                if runway_assigned:
                    response: ControllerResponseCall = ControllerResponseCall(self._radio.get_frequency(),
                                                                              FLIGHT_STATE.TAKEOFF, caller=self._name)
                    response.runway = runway_assigned
                    flight.runway = runway_assigned
                    if is_clean:
                        flight.status = FLIGHT_STATE.TAXI
                    else:
                        flight.status = FLIGHT_STATE.TAXI_HOLD
                        response.type_call = FLIGHT_STATE.TAXI_HOLD
                    response.grant(ClearanceCall(self._radio.get_frequency()), flight)
            elif flight.status == FLIGHT_STATE.HOLD_SHORT_RUNWAY:
                if self._base_ref.register_take_active(flight.size, flight.runway):
                    flight.status = FLIGHT_STATE.TAKE_RUNWAY
                    response: ControllerResponseCall = ControllerResponseCall(self._radio.get_frequency(),
                                                                              FLIGHT_STATE.TAKE_RUNWAY,
                                                                              caller=self._name)
                    response.grant(ClearanceCall(self._radio.get_frequency()), flight)
                    self._radio.respond(response)
                    time.sleep(0.5)

    def run(self) -> None:
        print('started ' + self._name + ' on freq: ' + str(self._radio.get_frequency()))
        self._radio.start()
        while not self._exit:
            self.receive_transmission()
            self.process_flight_queue()
        self._radio.shut_down()
        print('end ground...')
