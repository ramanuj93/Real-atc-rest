from elements import TextEngine
from elements.Entities import Airport, Runway, FLIGHT_STATE
from elements.Processors import TaxiCall, AIRCRAFT, FlightObject, HoldShortRunwayCall
import json
from flask import Flask, request
from flask_cors import CORS
from flask import send_file
import os
import tempfile
import recognition.listener as listen
import synthesis.speaker as speaker
import util.atc_log as logger
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import librosa
import random
from recognition import callinterpreter

#
nellis = Airport('Nellis', {'03R': Runway('03R', 4), '21R': Runway('21R', 4),
                            '03L': Runway('03L', 4), '21L': Runway('21L', 4)})
#
# inferno1 = FlightObject('Inferno 1', AIRCRAFT.HORNET, FLIGHT_STATE.NEW, 4)
# torch2 = FlightObject('Torch 2', AIRCRAFT.HORNET, FLIGHT_STATE.NEW, 4)
#
# print(TextEngine.TextEngine.CallToText(nellis.receive_transmission(TaxiCall(104, 'Nellis_Traffic', inferno1.callsign, inferno1.type_air, inferno1.size, '08R'))))
# print(TextEngine.TextEngine.CallToText(nellis.receive_transmission(HoldShortRunwayCall(104, 'Nellis_Traffic', inferno1.callsign, '08R'))))
# print(TextEngine.TextEngine.CallToText(nellis.receive_transmission(TaxiCall(104, 'Nellis_Traffic', torch2.callsign, torch2.type_air, torch2.size, '08R'))))
#
from recognition.Interpreter import Interpreter

nltk.download('stopwords')
nltk.download('punkt')
if __name__ == "__main__":
    stop_words = set(stopwords.words('english'))
    with open('./credentials.cred') as f:
        credentials = json.load(f)
        interpret_obj = callinterpreter.CallInterpreter(credentials)
        listener_obj = listen.Listener(credentials)
        listener_obj.listen()
        received = listener_obj.last_result()
        print(received)
        inter = Interpreter()
        call1 = inter.interpret_call(received)
        print(TextEngine.TextEngine.CallToText(nellis.receive_transmission(call1)))
