import json
import nltk
from nltk.corpus import stopwords
import recognition.listener as listen
from elements.AirTrafficManager import AirTrafficManager
from elements.Entities import Airport, Runway
import time
from recognition.Interpreter import Interpreter
import synthesis.speaker as speaker
from flask import Flask, request
from flask_cors import CORS
from flask import send_file
import tempfile
import librosa
import os

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
global atc_manager

app = Flask(__name__)


@app.route('/sendaudio', methods=['POST', 'GET'])
def send_audio():
    global atc_manager
    resp = request.files

    folderid = tempfile.mkdtemp()
    newfile = resp['recorded'].read()
    with open(folderid + '/ussr.wav', 'wb') as file:
        file.write(newfile)
    filew, _ = librosa.load(folderid + '/ussr.wav', sr=16000)
    librosa.output.write_wav(folderid + '/ussr3.wav', y=filew, sr=16000)

    atc_manager.speak_to(folderid + '/ussr3.wav')


    try:
        os.remove(folderid + "/ussr.wav")
        os.remove(folderid + "/ussr3.wav")
    except:
        print('error')

    return send_file(
        folderid + '/outputaudio.wav',
        mimetype="blob",
        as_attachment=True,
        attachment_filename="result.wav")


if __name__ == "__main__":
    stop_words = set(stopwords.words('english'))
    CORS(app, resources={r"/*": {"origins": "*"}})
    with open('./credentials.cred') as f:
        credentials = json.load(f)
        listener_obj = listen.Listener(credentials)
        speaker_obj = speaker.Speaker(credentials, '/home/ramanuj/box')
        interpret_agent = Interpreter()
        runway_3r = Runway('03R', 4)
        runway_21r = Runway('21R', 4)
        nellis = Airport('Nellis', {'03R': runway_3r})
        atc_manager = AirTrafficManager([nellis], speaker_obj, listener_obj)
        atc_manager.begin()
        time.sleep(2)
    app.run(host='0.0.0.0', debug=False)