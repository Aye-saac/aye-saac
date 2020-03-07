from pprint import pprint
# import speech_recognition  # Looks like speech_recognition is dead in the water
from pathlib import Path

from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from ayesaac.services_lib.queues.queue_manager import QueueManager


def callback_impl(data):
    # obtain audio from file:
    # todo use microphone
    project_root = Path(__file__).parent.parent.parent  # ayesaac
    audio_file = project_root / 'data' / 'test' / 'test-audio-query.wav'
    # recognize speech using IBM
    keyfilename = Path(__file__).parent / 'ibm_key'  # i.e. a file in the automatic_speech_recognition directory

    try:
        url = 'https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/0c812d73-03ef-4209-a78e-b73c4781f85a'
        with open(keyfilename, 'r') as keyfile:
            key = keyfile.read()

        authenticator = IAMAuthenticator(key)
        transcriber = SpeechToTextV1(authenticator=authenticator)
        transcriber.set_service_url(url)

        with open(audio_file, 'rb') as audio:  # open prerecorded file as binary
            try:
                transcribed_to_json = transcriber.recognize(audio=audio)
            except Exception as e:
                print("Watson error; {0}".format(e))

        text = str(transcribed_to_json)  # todo parse returned JSON
        print("Watson thinks you said " + text)
        data['query'] = text
    except Exception as e:
        print("ASR error; {0}".format(e))

    # fallback
    if 'query' not in data:
        data["query"] = "Is there a person in the kitchen ?"  # n.b. ibm wouldn't put a '?' here

    return data


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

    # inserted testing code
    # dicto = {}
    # print(callback_impl(dicto))  # TODO install pyaudio with poetry

    main()
