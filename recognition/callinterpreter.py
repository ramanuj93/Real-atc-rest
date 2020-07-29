from recognition.listener import Listener
from recognition.ATCCall import ATCCall
import nltk
from util import atc_log as logger
from util import Util as Util
import json

numbers = ['one', 'two', 'three', 'four', '1', '2', '3', '4']
aircarft_sym = '-aircraft-'
callsign_sym = '-callsign-'
runway_sym = '-runway-'
activity_sym = '-activity-'


class CallInterpreter:
    def __init__(self, credentials):
        nltk.download('stopwords')
        nltk.download('punkt')
        self._inputSpeech = None
        self._recievedText = None
        self._listener = Listener(credentials)
        self._recievedCall = ATCCall()

    def receive(self, audio):
        self._listener.listen(audio)
        self._recievedText = self._listener.last_result().lower()
        logger.log_event(self._recievedText)
        self.__extract_airport()
        self.__extract_runway()
        self.__extract_callsign()
        self.__extract_aircraft()

    def get_atc_call(self):
        return self._recievedCall

    def __extract_airport(self):
        # self._recievedText
        with open('references/runways.json') as f:
            runway_ref = json.load(f)
        self._recievedCall.airport = 'Nellis'

    def __extract_params(self, path, symbol, idx_map_func):
        with open(path) as f:
            param_ref = json.load(f)
            param_id, param_chosen = Util.extract_alias(param_ref, self._recievedText)
            if param_chosen:
                self._recievedText = str.replace(self._recievedText, param_chosen, symbol)
                filtered_call = self.__get_filtered_words()
                return filtered_call.index(symbol)

    def __extract_runway(self):
        def id_mapper(id):
            self._recievedText = str.replace(self._recievedText, runway_chosen, runway_sym)
            self._recievedCall.runway = runway_id
        self.__extract_params('references/runways.json', runway_sym )

    def __extract_callsign(self):
        with open('references/callsigns.json') as f:
            callsign_ref = json.load(f)
            callsign_id, callsign_chosen = Util.extract_alias(callsign_ref, self._recievedText)
            if callsign_chosen:
                self._recievedText = str.replace(self._recievedText, callsign_chosen, callsign_sym)
                filtered_call = self.__get_filtered_words()
                idx = filtered_call.index(callsign_sym)
                if filtered_call[idx + 1] in numbers:
                    self._recievedCall.callsign = "{0} {1}".format(callsign_id, filtered_call[idx + 1])
                    return

    def __extract_aircraft(self):
        with open('references/aircrafts.json') as f:
            airplane_ref = json.load(f)
            aircraft_id, aircraft_chosen = Util.extract_alias(airplane_ref, self._recievedText)
            if aircraft_chosen:
                self._recievedText = str.replace(self._recievedText, aircraft_chosen, aircarft_sym)
                filtered_call = self.__get_filtered_words()
                idx = filtered_call.index(aircarft_sym)
                if filtered_call[idx - 1] in numbers:
                    self._recievedCall.aircraft = [aircraft_id, filtered_call[idx + 1]]
                    return

    def __extract_activity(self):
        with open('references/activities.json') as f:
            activities_ref = json.load(f)
            activity_id, activity_chosen = Util.extract_alias(activities_ref, self._recievedText)
            if activity_chosen:
                self._recievedText = str.replace(self._recievedText, activity_chosen, activity_sym)
                filtered_call = self.__get_filtered_words()

    def __get_filtered_words(self):
        stop_words = set(nltk.corpus.stopwords.words('english'))
        word_tokens = nltk.word_tokenize(self._recievedText)
        return [w for w in word_tokens if w not in stop_words]


