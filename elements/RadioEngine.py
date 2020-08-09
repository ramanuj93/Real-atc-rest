import threading
import time
from typing import Dict
import util.atc_log as logger
from constants.HelperEntity import CallObject, ControllerResponseCall
from util.CallQueue import CallQueue


class Transmissions:
    def __init__(self, timeout: int = 300000):
        self._timeout = timeout
        self._incoming_queue: Dict[int, CallQueue] = {}
        self._outgoing_queue: Dict[int, CallQueue] = {}

    def add_request(self, call: CallObject):
        if call and call.freq > 0:
            if call.freq not in self._incoming_queue.keys():
                self._incoming_queue[call.freq] = CallQueue(50)
            self._incoming_queue[call.freq].push(call)
            if call.is_valid():
                logger.log_event('pushed call to request stack from ' + call.caller + ' on freq: ' + str(call.freq)
                                 + ' stack size is ' + str(self._incoming_queue[call.freq].size()))
            else:
                logger.log_event('pushed bad call to stack, size is ' + str(self._incoming_queue[call.freq].size()))

    def get_request(self, freq) -> CallObject:
        if freq > 0 and freq in self._incoming_queue.keys():
            result: CallObject = self._incoming_queue[freq].pop()
            if result:
                if result.get_age() > self._timeout:
                    return self.get_request(freq)
                if result.is_valid():
                    logger.log_event('retrieved request from ' + result.caller + ' on  freq: ' + str(freq)
                                     + ' stack size is ' + str(self._incoming_queue[freq].size()))
                else:
                    logger.log_event('retrieved bad call from stack, size is ' + str(self._incoming_queue[freq].size()))
            return result

    def add_response(self, response: ControllerResponseCall):
        if response and response.freq > 0:
            if response.freq not in self._outgoing_queue.keys():
                self._outgoing_queue[response.freq] = CallQueue(50)
            self._outgoing_queue[response.freq].push(response)
            print('added response for freq: ' + str(response.freq) + ' stack size is '
                  + str(self._outgoing_queue[response.freq].size()))

    def get_responses(self) -> [ControllerResponseCall]:
        all_responses = []
        for response_freq in self._outgoing_queue.keys():
            responses = self._outgoing_queue[response_freq]
            if responses:
                while responses.size() > 0:
                    all_responses.append(responses.pop())

        return all_responses


global_transmission_ref: Transmissions = Transmissions()


class RadioEngine(threading.Thread):
    def __init__(self, freq, max_buffer=50):
        threading.Thread.__init__(self)
        self._freq = freq
        self._transmission_ref: Transmissions = global_transmission_ref
        self._message_queue = CallQueue(max_buffer)
        self._interval: float = 0.5
        self._exit: bool = False

    def get_frequency(self):
        return self._freq

    def listen(self) -> CallObject:
        return self._message_queue.pop()

    def respond(self, response: ControllerResponseCall):
        self._transmission_ref.add_response(response)

    def shut_down(self):
        self._exit = True

    def run(self):
        while not self._exit:
            time.sleep(self._interval)
            new_call = self._transmission_ref.get_request(self._freq)
            if new_call:
                self._message_queue.push(new_call)


class EmissionsControl:

    @staticmethod
    def transmit_request(request: CallObject):
        global_transmission_ref.add_request(request)

    @staticmethod
    def broadcast_response() -> [ControllerResponseCall]:
        return global_transmission_ref.get_responses()


