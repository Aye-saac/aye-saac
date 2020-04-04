from enum import Enum, auto
from pprint import pprint
from pathlib import Path

from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from playsound import playsound

from ayesaac.services_lib.queues.queue_manager import QueueManager
import ayesaac.services.automatic_speech_recognition.speech_recognition.microphone as mic
import ayesaac.services.automatic_speech_recognition.speech_recognition.recognizer as recogniton

from utils.ibm_key import get_api_key


class Level(Enum):
    """
    This Automatic Speech Recognition (ASR) service has 3 modes of operation to save us from getting a large bill:
        1. Total fake; ASR will output the same string in every case.
        2. Wet-run test; as in 'not a dry run'. Uses a prerecorded message, but still sends it through the web api.
        3. The real deal; record user speech through an attached microphone.
    """
    CHEAP_TEST = auto()
    FULL_TEST = auto()
    LIVE_RECORDINGS = auto()


class Dinger:
    """
    Make the thing go ding when ready to record/finished recording.
    """
    project_root = Path(__file__)/ '..' / '..' / '..' / '..'
    data_dir = project_root / 'ayesaac' / 'data'
    ding_in = data_dir / 'ayesaac-ding-in.wav'
    ding_out = data_dir / 'ayesaac-ding-out.wav'

    def __init__(self):
        pass

    def __enter__(self):
        playsound(self.ding_in)

    def __exit__(self, exc_type, exc_val, exc_tb):
        playsound(self.ding_out)


def callback_impl(data, functionality_level=Level.LIVE_RECORDINGS):
    """
    A function that removes ASR specific code from the boilerplate RabbitMQ queue listener code.
    :param data: The dictionary passed to the next service. ASR results go in here.
    :param functionality_level: exposed for testing - see the top of this file.
    :return: Nothing
    """
    if functionality_level != Level.CHEAP_TEST:
        record_and_transcribe(data, functionality_level)

    # fallback
    if 'query' not in data:
        data["query"] = "Is there a person in the kitchen ?"  # n.b. ibm wouldn't put a '?' here

    return data


def record_and_transcribe(data, functionality_level: Level):
    """

    :param data: The big cheese dictionary that gets passed between microservices.
    :param functionality_level:
    :return: nothing, results are inserted into the data object
    """

    try:

        if functionality_level == Level.LIVE_RECORDINGS:
            wav_audio = record_from_microphone()
            transcribed_to_json = use_ibm_api(wav_audio)

        else:
            # obtain audio from file:
            project_root = Path(__file__).parent.parent.parent  # ayesaac
            audio_file = project_root / 'data' / 'test' / 'test-audio-query.wav'

            with open(audio_file, 'rb') as audio_file:  # open prerecorded file as binary
                transcribed_to_json = use_ibm_api(audio_file)

        # The api returns a dict containing 'results' and some metadata, then a list of options ordered by likelihood.
        # This just takes the top result's text and ignores its probability.
        transcript = transcribed_to_json.get_result()['results'][0]['alternatives'][0]['transcript']

        print("Watson thinks you said " + transcript)
        data['query'] = transcript
    except Exception as e:
        print("ASR error; {0}".format(e))
        raise e


def use_ibm_api(audio_file):
    """
    Recognize speech using IBM
    :param audio_file: .wav audio as bytes to send to IBM
    :return: transcribed text
    """

    # this url is unique to HM's account
    url = 'https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/0c812d73-03ef-4209-a78e-b73c4781f85a'
    key = get_api_key()

    authenticator = IAMAuthenticator(key)
    transcriber = SpeechToTextV1(authenticator=authenticator)
    transcriber.set_service_url(url)
    try:
        transcribed_to_json = transcriber.recognize(audio=audio_file)
    except Exception as e:
        print("Watson error; {0}".format(e))
        transcribed_to_json = []
    return transcribed_to_json


def record_from_microphone():
    r = recogniton.Recognizer()
    with mic.Microphone() as source, Dinger():
        print("Say something!")
        audio = r.listen(source)
    print("Ok - processing...")
    return audio.get_wav_data()


class AutomaticSpeechRecognition(object):
    """
    The class AutomaticSpeechRecognition purpose is to convert speech to text.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "NaturalLanguageUnderstanding"])

    def callback(self, body, **_):
        """
        The function run by the queue manager when a message for this service reaches the front.

        :param body: a dictionary containing info required. This service expects to be the first run, so
                     only requires a "path_done" list to be inside.
        :param _:    Other callbacks may take more params. They should be ignored in this case.
        :return: None
        """
        pprint(body)
        body = callback_impl(body)

        pprint(body["query"])
        body["path_done"].append(self.__class__.__name__)
        self.queue_manager.publish("NaturalLanguageUnderstanding", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    automatic_speech_recognition = AutomaticSpeechRecognition()
    automatic_speech_recognition.run()


if __name__ == "__main__":
    main()
