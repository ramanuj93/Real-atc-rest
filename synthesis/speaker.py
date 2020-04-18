import azure.cognitiveservices.speech as speechsdk


class Speaker:

    def __init__(self, credentials):
        speech_key = credentials['speech_key']
        service_region = credentials['service_region']
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        voice = "Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)"
        speech_config.speech_synthesis_voice_name = voice
        file_name = "outputaudio.wav"
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
        self.__speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)
        self.__result = None

    def synthesise(self, text):
        self.__result = self.__speech_synthesizer.speak_text_async(text)

    def speak(self):
        result = self.__result.get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            self.__result = result
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
            print("Did you update the subscription info?")










# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and service region (e.g., "westus").

# Creates a speech synthesizer using the default speaker as audio output.

# Receives a text from console input.
# print("Type some text that you want to speak...")
# text = input()

# Synthesizes the received text to speech.
# The synthesized speech is expected to be heard on the speaker with this line executed.

# Checks result.