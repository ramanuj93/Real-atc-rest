import json
import nltk

from constants.EnumATC import AIRCRAFT, FLIGHT_STATE
from constants.HelperEntity import TaxiCall, CallObject, HoldShortRunwayCall, RunwayEnterCall
from util import Util as Util

numbers = ['one', 'two', 'three', 'four', '1', '2', '3', '4']
aircraft_sym = '-aircraft-'
callsign_sym = '-callsign-'
runway_sym = '-runway-'
activity_sym = '-activity-'


class Interpreter:

    def __init__(self):
        nltk.download('stopwords')
        nltk.download('punkt')
        with open('references/aircrafts.json') as f:
            self._known_aircraft = json.load(f)
        with open('references/runways.json') as f:
            self._known_runways = json.load(f)
        with open('references/callsigns.json') as f:
            self._accepted_callsigns = json.load(f)
        with open('references/activities.json') as f:
            self._known_activities = json.load(f)
        return

    def __recognize_aircraft(self, segment):
        aircraft_id, aircraft_chosen = Util.extract_alias(self._known_aircraft, segment)
        if aircraft_id:
            try:
                segment = str.replace(segment, aircraft_chosen, aircraft_sym)
                filtered_call = self.__get_filtered_words(segment)
                idx = filtered_call.index(aircraft_sym)
                return aircraft_id, (numbers.index(filtered_call[idx - 1]) % 4 + 1)
            except ValueError:
                return aircraft_id, None
        return None, None

    def __recognize_airport(self, segment):
        return 'Nellis'

    def __recognize_runway(self, segment):
        runway_id, runway_chosen = Util.extract_alias(self._known_runways['Nellis'], segment)
        if runway_id:
            return runway_id
        return None

    def __recognize_callsign(self, segment):
        callsign_id, callsign_chosen = Util.extract_alias(self._accepted_callsigns, segment)
        if callsign_chosen:
            try:
                segment = str.replace(segment, callsign_chosen, callsign_sym)
                filtered_call = self.__get_filtered_words(segment)
                idx = filtered_call.index(callsign_sym)
                return callsign_id, (numbers.index(filtered_call[idx + 1]) % 4 + 1)
            except ValueError:
                return callsign_id, None
        return None, None

    def __recognize_activity(self, segment):
        activity_chosen, _ = Util.extract_alias(self._known_activities, segment)
        if activity_chosen:
            return activity_chosen
        return None

    def __get_filtered_words(self, received_text):
        stop_words = set(nltk.corpus.stopwords.words('english'))
        word_tokens = nltk.word_tokenize(received_text)
        return [w for w in word_tokens if w not in stop_words]

    def __get_recognized_aircraft_type(self, aircraft):
        if aircraft == "F-18":
            return AIRCRAFT.HORNET
        elif aircraft == "F-16":
            return AIRCRAFT.VIPER
        elif aircraft == "F-14":
            return AIRCRAFT.TOMCAT
        else:
            return AIRCRAFT.UNKNOWN

    def interpret_call(self, sentence):
        sentence = sentence.lower()
        aircraft, aircraft_num = self.__recognize_aircraft(sentence)
        callsign, callsign_num = self.__recognize_callsign(sentence)
        airport = self.__recognize_airport(sentence)
        runway = self.__recognize_runway(sentence)
        activity = self.__recognize_activity(sentence)

        flight_name = None
        if callsign and callsign_num:
            flight_name = '{0} {1}'.format(callsign, callsign_num)
        elif callsign:
            flight_name = callsign

        flight_size = 0
        if aircraft:
            if aircraft_num:
                flight_size = aircraft_num

        if activity == "taxi":
            return TaxiCall(104, airport, flight_name, self.__get_recognized_aircraft_type(aircraft),
                            flight_size, runway)
        if activity == "hold":
            return HoldShortRunwayCall(104, airport, flight_name, runway)

        if activity == "active":
            return RunwayEnterCall(104, airport, flight_name)

        return CallObject(104, FLIGHT_STATE.UNKNOWN)
