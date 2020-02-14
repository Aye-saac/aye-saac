
from pprint import pprint

from services_lib.queues.queue_manager import QueueManager

import os
from gtts import gTTS
from playsound import playsound

class TextToSpeech(object):
    """
    The class TextToSpeech purpose is to deliver an audio from a given text.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__])

    def callback(self, body, **_):
        pprint(body)
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
