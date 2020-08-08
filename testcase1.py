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
from recognition import callinterpreter
from recognition.Interpreter import Interpreter

runway_3r = Runway('03R', 4)
runway_21r = Runway('21R', 4)
nellis = Airport('Nellis', {'03R': runway_3r})
manager = AirTrafficManager([nellis])


nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
with open('./credentials.cred') as f:
    credentials = json.load(f)
    interpret_obj = callinterpreter.CallInterpreter(credentials)
    listener_obj = listen.Listener(credentials)
    inter = Interpreter()

    manager.begin()
    time.sleep(2)

    listener_obj.listen()
    received = listener_obj.last_result()
    print(received)
    call1 = inter.interpret_call(received)
    EmissionsControl.transmit_request(call1)

    for line in sys.stdin:
        if '0' == line.rstrip():
            break
        elif '1' == line.rstrip():
            listener_obj.listen()
            received = listener_obj.last_result()
            print('Your call: ' + received)
            call1 = inter.interpret_call(received)
            EmissionsControl.transmit_request(call1)
        elif '2' == line.rstrip():
            responses: [ControllerResponseCall] = EmissionsControl.broadcast_response()
            if responses:
                for response in responses:
                    print(TextEngine.CallToText(response))

    manager.shut_down()
    print("Done")



