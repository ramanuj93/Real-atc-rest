from flask import Flask, request
from flask_cors import CORS
from flask import send_file
import json
import recognition.listener as listen
import synthesis.speaker as speaker
import telemetry.atc_log as logger
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import wave
import librosa
import librosa.display

global credentials
global listener_obj
global speaker_obj
global callsign
global callsign_count
global aircraft
global aircraft_count
global runway

app = Flask(__name__)

stop_words = set(stopwords.words('english'))



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
            callsign_count = filtered_sentence[i+1]






@app.route('/sendaudio', methods=['POST', 'GET'])
def send_audio():
    resp = request.files
    print(resp)
    newfile = resp['recorded'].read()
    with open('ussr.wav', 'wb') as file:
        file.write(newfile)
    filew, _ = librosa.load('ussr.wav', sr=16000)
    librosa.output.write_wav('ussr3.wav', y=filew, sr=16000)

    with open('./credentials.cred') as f:
        global speaker_obj
        global listener_obj

        credentials = json.load(f)
        listener_obj = listen.Listener(credentials, 'ussr3.wav')
        speaker_obj = speaker.Speaker(credentials)

    listener_obj.listen()
    received = listener_obj.last_result()
    transform(received)

    speaker_obj.synthesise(
        callsign + callsign_count + "!" + " Nellis Tower, taxi to and hold short of, runway " + runway)
    speaker_obj.speak()
    return send_file(
        'outputaudio.wav',
        mimetype="blob",
        as_attachment=True,
        attachment_filename="result.wav")


CORS(app, resources={r"/*": {"origins": "*"}})
app.run(port=80, debug=False)

