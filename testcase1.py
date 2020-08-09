import json
import nltk
from nltk.corpus import stopwords
import recognition.listener as listen
from constants.HelperEntity import ControllerResponseCall
from elements.AirTrafficManager import AirTrafficManager
from elements.Entities import Airport, Runway
import time
import sys
from elements.RadioEngine import EmissionsControl
from elements.TextEngine import TextEngine
from recognition.Interpreter import Interpreter
import synthesis.speaker as speaker


nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
with open('./credentials.cred') as f:
    credentials = json.load(f)
    listener_obj = listen.Listener(credentials)
    speaker_obj = speaker.Speaker(credentials, '/home/ramanuj/box')
    inter = Interpreter()
    runway_3r = Runway('03R', 4)
    runway_21r = Runway('21R', 4)
    nellis = Airport('Nellis', {'03R': runway_3r})
    atc_manager = AirTrafficManager([nellis], speaker_obj)

    atc_manager.begin()
    time.sleep(2)

    listener_obj.test_listen()
    received = listener_obj.last_result()
    print(received)
    call1 = inter.interpret_call(received)
    EmissionsControl.transmit_request(call1)

    for line in sys.stdin:
        if '0' == line.rstrip():
            break
        elif '1' == line.rstrip():
            listener_obj.test_listen()
            received = listener_obj.last_result()
            print('Your call: ' + received)
            call1 = inter.interpret_call(received)
            EmissionsControl.transmit_request(call1)
        elif '2' == line.rstrip():
            listener_obj.test_listen()
            received = listener_obj.last_result()
            print('Your call: ' + received)
            call1 = inter.interpret_call(received, 105)
            EmissionsControl.transmit_request(call1)
        elif 'x' == line.rstrip():
            responses: [ControllerResponseCall] = EmissionsControl.broadcast_response()
            if responses:
                for response in responses:
                    print(TextEngine.CallToText(response))

    atc_manager.shut_down()
    print("Done")



