
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager

import os
from gtts import gTTS
from playsound import playsound


class TextToSpeech(object):
    """
    The class TextToSpeech purpose is to deliver an audio from a given text.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "AppInterface"])

    def client_handles_tts(self, body):
        """
        If this is being run as a web app, there are probably no speakers to play sound out of here on the server.
        The website can do TTS client-side, so just tell the server (via AppInterface) that it can respond.
        :param body: The full monty of all data produced by the service pipeline
        :return: None
        """
        body['path_done'].append(self.__class__.__name__)
        self.queue_manager.publish("AppInterface", body)

    def callback(self, body, **_):
        pprint(body)
        if "run_as_webservice" in body:
            self.client_handles_tts(body)
        else:
            if "response" in body:
                gTTS(text=body['response'], lang='en', slow=False).save("audio.mp3")
                playsound('audio.mp3')
                os.remove('audio.mp3')
            body['path_done'].append(self.__class__.__name__)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    text_to_speech = TextToSpeech()
    text_to_speech.run()


if __name__ == "__main__":
    main()
