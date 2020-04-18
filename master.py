import json
import recognition.listener as listen
import synthesis.speaker as speaker
import telemetry.atc_log as logger
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

global credentials
global listener_obj
global speaker_obj
global callsign
global callsign_count
global aircraft
global aircraft_count

stop_words = set(stopwords.words('english'))


def domain_aircraft(atc_call):
    global aircraft

    airplane_ref = {}
    with open('references/aircrafts.json') as f:
        airplane_ref = json.load(f)
    for aircraft in airplane_ref:
        matched = [x for x in airplane_ref[aircraft] if x in atc_call]
        if matched:
            logger.log_event("Found " + aircraft)

            atc_call = atc_call.replace(matched[0], " aircraft ")
    return atc_call

def domain_callsigns(atc_call):
    global speaker_obj
    global callsign

    callsign_ref = {}
    with open('references/callsigns.json') as f:
        callsign_ref = json.load(f)

    for callsign in callsign_ref:
        matched = [x for x in callsign_ref[callsign] if x in atc_call]
        if matched:
            logger.log_event("Found " + callsign)
            speaker_obj.synthesise(callsign + " flight!" + " Nellis Tower, taxi to and hold short of, runway 3, Left.")
            speaker_obj.speak()
            atc_call = atc_call.replace(matched[0], " callsign ")
    return atc_call


def transform(recieved_call):
    recieved_call = recieved_call.lower()
    received = domain_aircraft(recieved_call)
    received = domain_callsigns(received)
    word_tokens = word_tokenize(received)
    filtered_sentence = [w for w in word_tokens if w not in stop_words]
    logger.log_event("Recognized: {}".format(filtered_sentence))
    for e,i in filtered_sentence:
        print(e)
        print(i)


with open('./credentials.cred') as f:
    global speaker_obj
    global listener_obj

    credentials = json.load(f)
    listener_obj = listen.Listener(credentials)
    speaker_obj = speaker.Speaker(credentials)

listener_obj.listen()
received = listener_obj.last_result()

transform(received)

