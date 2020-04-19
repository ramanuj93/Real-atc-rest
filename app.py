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

    recieved_call = recieved_call.lower()
    received = domain_aircraft(recieved_call)
    received = domain_callsigns(received)
    received = domain_runway(received)
    word_tokens = word_tokenize(received)
    filtered_sentence = [w for w in word_tokens if w not in stop_words]
    logger.log_event("Recognized: {}".format(filtered_sentence))
    for i in range(len(filtered_sentence)):
        if (filtered_sentence[i] == "callsign_ref"):
            callsign_count = filtered_sentence[i + 1]


@app.route('/sendaudio', methods=['POST', 'GET'])
def send_audio():
    global listener_obj
    global speaker_obj

    resp = request.files
    print(resp)

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
    transform(received)
    try:
        os.remove(folderid + "/ussr.wav")
        os.remove(folderid + "/ussr3.wav")
    except:
        print('error')
    finally:
        print('done')

    speaker_obj.synthesise(
        callsign + callsign_count + "!" + " Nellis Tower, taxi to and hold short of runway " + runway)
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
