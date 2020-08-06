from flask import Flask, request
from flask_cors import CORS
from flask import send_file
import json
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


app = Flask(__name__)

global credentials
global listener_obj
global speaker_obj
global callsign
global callsign_count
global aircraft
global aircraft_count
global runway
global flight_runway_map


@app.route('/sendaudio', methods=['POST', 'GET'])
def send_audio():
    global listener_obj
    global speaker_obj
    global callsign
    global callsign_count
    global runway
    global aircraft
    global interpret_obj

    resp = request.files

    folderid = tempfile.mkdtemp()
    newfile = resp['recorded'].read()
    with open(folderid + '/ussr.wav', 'wb') as file:
        file.write(newfile)
    filew, _ = librosa.load(folderid + '/ussr.wav', sr=16000)
    librosa.output.write_wav(folderid + '/ussr3.wav', y=filew, sr=16000)

    listener_obj = listen.Listener(credentials)
    speaker_obj = speaker.Speaker(credentials, folderid + '/')

    # listener_obj.listen(folderid + '/ussr3.wav')
    # received = listener_obj.last_result()
    # print(received)
    callsign = None
    callsign_count = None
    runway = None
    aircraft = None
    interpret_obj.receive(folderid + '/ussr3.wav')
    stuff = interpret_obj.get_atc_call()
    print(interpret_obj._recievedText)
    print(interpret_obj.get_atc_call().airport)
    print(interpret_obj.get_atc_call().runway)
    print(interpret_obj.get_atc_call().callsign)
    print(interpret_obj.get_atc_call().aircraft)

    return 'done'
    return send_file(
        folderid + '/outputaudio.wav',
        mimetype="blob",
        as_attachment=True,
        attachment_filename="result.wav")


if __name__ == "__main__":
    global credentials
    global interpret_obj
    stop_words = set(stopwords.words('english'))
    CORS(app, resources={r"/*": {"origins": "*"}})
    with open('./credentials.cred') as f:
        global speaker_obj
        global listener_obj
        credentials = json.load(f)
        interpret_obj = callinterpreter.CallInterpreter(credentials)

    app.run(host='0.0.0.0', debug=True)
