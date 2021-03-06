import azure.cognitiveservices.speech as speechsdk


class Listener:
    def __init__(self, credentials, audio):
        speech_key = credentials['speech_key']
        service_region = credentials['service_region']
        self._speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        self.audioSource = audio
        self._audio_config = None
        self._speech_recognizer = None
        self.__recognized = ''

    def listen(self):
        print("Say something...")
        # Creates a recognizer with the given settings
        self._audio_config = speechsdk.audio.AudioConfig(filename=self.audioSource)
        self._speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self._speech_config, audio_config=self._audio_config)
        # Starts speech recognition, and returns after a single utterance is recognized. The end of a
        # single utterance is determined by listening for silence at the end or until a maximum of 15
        # seconds of audio is processed.  The task returns the recognition text as result.
        # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
        # shot recognition like command or query.
        # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
        result = self._speech_recognizer.recognize_once()

        # Creates an instance of a speech config with specified subscription key and service region.
        # Replace with your own subscription key and service region (e.g., "westus").

        # Checks result.
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            self.__recognized = result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(result.no_match_details))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

    def last_result(self):
        return self.__recognized

