from flask import Flask, request
from flask_cors import CORS
from flask import send_file
import json
import os
import tempfile
import recognition.listener as listen
import synthesis.speaker as speaker
import telemetry.atc_log as logger
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import librosa
import random

global credentials
global listener_obj
global speaker_obj
global callsign
global callsign_count
global aircraft
global aircraft_count
global runway
global flight_runway_map

flight_runway_map = dict()

nltk.download('stopwords')
nltk.download('punkt')

app = Flask(__name__)


def domain_aircraft(atc_call):
    global aircraft

    airplane_ref = {}
    with open('references/aircrafts.json') as f:
        airplane_ref = json.load(f)
    for object in airplane_ref:
        matched = [x for x in airplane_ref[object] if x in atc_call]
        if matched:
            logger.log_event("Found " + object)
            aircraft = object
            atc_call = atc_call.replace(matched[0], " aircraft_ref ")
    return atc_call


def domain_callsigns(atc_call):
    global callsign

    callsign_ref = {}
    with open('references/callsigns.json') as f:
        callsign_ref = json.load(f)

    for name in callsign_ref:
        matched = [x for x in callsign_ref[name] if x in atc_call]
        if matched:
            logger.log_event("Found " + name)
            callsign = name
            atc_call = atc_call.replace(matched[0], " callsign_ref ")
    return atc_call


def domain_runway(atc_call):
    global runway

    with open('references/runways.json') as f:
        runway_ref = json.load(f)

    for name in runway_ref:
        matched = [x for x in runway_ref[name] if x in atc_call]
        if matched:
            logger.log_event("Found " + name)
            runway = name
            atc_call = atc_call.replace(matched[0], " runway_ref ")
            break
    return atc_call


def transform(recieved_call):
    global callsign
    global callsign_count

    received = domain_aircraft(recieved_call)
    received = domain_callsigns(received)
    received = domain_runway(received)
    word_tokens = word_tokenize(received)
    filtered_sentence = [w for w in word_tokens if w not in stop_words]
    logger.log_event("Recognized: {}".format(filtered_sentence))
    for i in range(len(filtered_sentence)):
        if (filtered_sentence[i] == "callsign_ref"):
            callsign_count = filtered_sentence[i + 1]


def isTaxi(recieved_call):
    if "ready" in recieved_call:
        if "taxi" in recieved_call:
            return True

    return False


def isHoldShort(recieved_call):
    if "holding" in recieved_call:
        if "short" in recieved_call:
            return True

    return False


@app.route('/talkatc', methods=['POST'])
def talkatc():
    global listener_obj
    global speaker_obj
    global callsign
    global callsign_count
    global runway
    global aircraft
    global flight_runway_map

    resp = request.files

    folderid = tempfile.mkdtemp()
    newfile = resp['recorded'].read()
    with open(folderid + '/ussr.wav', 'wb') as file:
        file.write(newfile)
    filew, _ = librosa.load(folderid + '/ussr.wav', sr=16000)
    librosa.output.write_wav(folderid + '/ussr3.wav', y=filew, sr=16000)

    listener_obj = listen.Listener(credentials, folderid + '/ussr3.wav')
    speaker_obj = speaker.Speaker(credentials, folderid + '/')

    listener_obj.listen()
    received = listener_obj.last_result()
    print(received)
    callsign = None
    callsign_count = None
    runway = None
    aircraft = None
    received = received.lower()
    transform(received)

    try:
        os.remove(folderid + "/ussr.wav")
        os.remove(folderid + "/ussr3.wav")
    except:
        print('error')

    voice_text = 'This is Nellis Tower? Say again-please?'

    if isTaxi(received):
        voice_text = callsign + callsign_count + "!" + " Nellis Tower, taxi-to-and-hold-short-of-runway " + runway
        if callsign and aircraft and runway:
            flight_runway_map[runway] = [callsign + callsign_count, aircraft]

    elif isHoldShort(received):

        if callsign and runway:
            if runway not in flight_runway_map:
                voice_text = callsign + "-" + callsign_count + " What-the-Fuck?... who told you to get there? Ask clearance to taxi first!"
            elif flight_runway_map[runway] and flight_runway_map[runway][0] == (callsign + callsign_count):
                voice_text = "{0}-{1}, Nellis Tower, Cleared for takeoff: runway {2}, Switch-to-departure on two-five-zero".format(
                    callsign, callsign_count, runway)
                flight_runway_map[runway] = None
            else:
                voice_text = "Nope! Hang on..."


    v1 = "Runway 3-left via delta-foxtrot. Inferno-1!"
    v2 = "Inferno-1, Nellis Tower, Cleared for takeoff: runway 3-left, Switch-to-departure on two five zero"
    speaker_obj.synthesise(voice_text)
    speaker_obj.speak()

    return send_file(
        folderid + '/outputaudio.wav',
        mimetype="blob",
        as_attachment=True,
        attachment_filename="result.wav")


@app.route('/sendaudio', methods=['POST', 'GET'])
def send_audio():
    global listener_obj
    global speaker_obj
    global callsign
    global callsign_count
    global runway
    global aircraft

    resp = request.files

    folderid = tempfile.mkdtemp()
    newfile = resp['recorded'].read()
    with open(folderid + '/ussr.wav', 'wb') as file:
        file.write(newfile)
    filew, _ = librosa.load(folderid + '/ussr.wav', sr=16000)
    librosa.output.write_wav(folderid + '/ussr3.wav', y=filew, sr=16000)

    listener_obj = listen.Listener(credentials, folderid + '/ussr3.wav')
    speaker_obj = speaker.Speaker(credentials, folderid + '/')

    listener_obj.listen()
    received = listener_obj.last_result()
    print(received)
    callsign = None
    callsign_count = None
    runway = None
    aircraft = None
    received = received.lower()
    transform(received)

    try:
        os.remove(folderid + "/ussr.wav")
        os.remove(folderid + "/ussr3.wav")
    except:
        print('error')

    voice_text = 'This is Nellis Tower? Say again-please?'
    if callsign and runway:
        voice_text = callsign + callsign_count + "!" + " Nellis Tower, taxi-to-and-hold-short-of-runway " + runway
    elif callsign and aircraft:
        voice_text = callsign + callsign_count + "! Nellis Tower, say which-runway-please?"
    elif callsign:
        voice_text = callsign + callsign_count + "! Nellis Tower, repeatlast?"
    v1 = "Runway 3-left via delta-foxtrot. Inferno-1!"
    v2 = "Inferno-1, Nellis Tower, Cleared for takeoff runway: 3-left, Switch-to-departure on 2-5-0"
    speaker_obj.synthesise(voice_text)
    speaker_obj.speak()

    return send_file(
        folderid + '/outputaudio.wav',
        mimetype="blob",
        as_attachment=True,
        attachment_filename="result.wav")


if __name__ == "__main__":
    global credentials
    stop_words = set(stopwords.words('english'))
    CORS(app, resources={r"/*": {"origins": "*"}})
    with open('./credentials.cred') as f:
        global speaker_obj
        global listener_obj

        credentials = json.load(f)
    app.run(host='0.0.0.0', debug=False)
