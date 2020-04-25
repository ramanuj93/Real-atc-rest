from recognition.listener import Listener
from recognition.ATCCall import ATCCall
import nltk
from util import atc_log as logger
from util import Util as Util
import json



class Router:
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

    def __extract_airport(self):
        # self._recievedText
        with open('../references/runways.json') as f:
            runway_ref = json.load(f)
        self._recievedCall.airport = runway_ref[0]

    def __extract_runway(self):
        with open('../references/runways.json') as f:
            runway_ref = json.load(f)
            airport = self._recievedCall.airport
            if airport in runway_ref:
                runway_chosen = Util.extract_alias(runway_ref[airport], self._recievedText)
                if runway_chosen:
                    self._recievedCall.runway = runway_chosen

    def __extract_callsign(self):
        with open('../references/callsigns.json') as f:
            callsign_ref = json.load(f)
            callsign_chosen = Util.extract_alias(callsign_ref, self._recievedText)
            if callsign_chosen:
                filtered_call = self.__get_filtered_words()
                idx = filtered_call.index(callsign_chosen)
                if filtered_call[idx + 1] in ['one', 'two', 'three', '1', '2', '3']:
                    self._recievedCall.callsign = "{0} {1}".format(callsign_chosen, filtered_call[idx + 1])
                    return

    def __extract_aircraft(self):
        with open('../references/aircrafts.json') as f:
            airplane_ref = json.load(f)
            aircraft_chosen = Util.extract_alias(airplane_ref, self._recievedText)
            if aircraft_chosen:
                filtered_call = self.__get_filtered_words()
                idx = filtered_call.index(aircraft_chosen)
                if filtered_call[idx - 1] in ['one', 'two', 'three', 'four', '1', '2', '3', '4']:
                    self._recievedCall.aircraft = [aircraft_chosen, filtered_call[idx + 1]]
                    return

    def __get_filtered_words(self):
        stop_words = set(nltk.stopwords.words('english'))
        word_tokens = nltk.word_tokenize(self._recievedText)
        return [w for w in word_tokens if w not in stop_words]





    def __extract_callsign(self):
        with open('../references/callsigns.json') as f:
            callsign_ref = json.load(f)


