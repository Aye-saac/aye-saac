import os
import subprocess
from enum import Enum, auto
from pathlib import Path
from pprint import pprint

from dotenv import find_dotenv, load_dotenv
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1

from ayesaac.queue_manager.queue_manager import QueueManager
from ayesaac.utils.config import Config
from ayesaac.utils.logger import get_logger


config = Config()


logger = get_logger(__file__)

load_dotenv(find_dotenv())


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


# class Dinger:
#     """
#     Make the thing go ding when ready to record/finished recording.
#     """

#     project_root = Path(__file__) / ".." / ".." / ".." / ".."
#     data_dir = project_root / "ayesaac" / "data"
#     ding_in = str(data_dir / "ayesaac-ding-in.wav")
#     ding_out = str(data_dir / "ayesaac-ding-out.wav")

#     def __init__(self):
#         pass

#     def __enter__(self):
#         playsound(self.ding_in)

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         playsound(self.ding_out)


# def callback_impl(data, functionality_level=Level.LIVE_RECORDINGS):
#     """
#     A function that removes ASR specific code from the boilerplate RabbitMQ queue listener code.
#     :param data: The dictionary passed to the next service. ASR results go in here.
#     :param functionality_level: exposed for testing - see the top of this file.
#     :return: Nothing
#     """
#     if functionality_level != Level.CHEAP_TEST:
#         record_and_transcribe(data, functionality_level)

#     # fallback
#     if "query" not in data:
#         data[
#             "query"
#         ] = "Is there a person in the kitchen ?"  # n.b. ibm wouldn't put a '?' here

#     return data


# def record_and_transcribe(data, functionality_level: Level):
#     """

#     :param data: The big cheese dictionary that gets passed between microservices.
#     :param functionality_level:
#     :return: nothing, results are inserted into the data object
#     """

#     try:

#         if functionality_level == Level.LIVE_RECORDINGS:
#             wav_audio = get_audio(data)  #
#             transcribed_to_json = use_ibm_api(wav_audio)

#         else:
#             # obtain audio from file:
#             project_root = Path(__file__).parent.parent.parent  # ayesaac
#             audio_file = project_root / "data" / "test" / "test-audio-query.wav"

#             with open(
#                 audio_file, "rb"
#             ) as audio_file:  # open prerecorded file as binary
#                 transcribed_to_json = use_ibm_api(audio_file)

#         # The api returns a dict containing 'results' and some metadata, then a list of options ordered by likelihood.
#         # This just takes the top result's text and ignores its probability.
#         transcript = transcribed_to_json.get_result()["results"][0]["alternatives"][0][
#             "transcript"
#         ]

#         print("Watson thinks you said " + transcript)
#         data["query"] = transcript
#     except Exception as e:
#         print("ASR error; {0}".format(e))
#         raise e


def get_audio(body):
    if "run_as_webservice" in body:
        # audio data is in the supplied body
        return get_wav_from_web_input(body)
    else:
        raise NotImplementedError(
            "The ability to record from the microphone was disabled because of dependency installation issues. "
        )
        # get it live
        # return record_from_microphone()


def get_wav_from_web_input(body):
    """
    Voice files from the web come in ogg format.
    IBM takes files in wav format. Convert here.
    :param body: dict that passes between services
    :return: wav bytestream
    """
    voice_file = body["voice_file"]  # expected to be a path to a .ogg file

    out_name = f"{voice_file[:-4]}.wav"

    # https://stackoverflow.com/a/60332477
    subprocess.call(["ffmpeg", "-i", f"{voice_file}", f"{out_name}"])

    with open(out_name, "rb") as f:
        wav = f.read()

    # cleanup temp files - todo use the proper tempfile library
    os.remove(out_name)
    os.remove(voice_file)
    return wav


def use_ibm_api(audio_file):
    """
    Recognize speech using IBM
    :param audio_file: .wav audio as bytes to send to IBM
    :return: transcribed text
    """

    url = config.ibmwatson.endpoint
    key = config.ibmwatson.api_key

    authenticator = IAMAuthenticator(key)
    transcriber = SpeechToTextV1(authenticator=authenticator)
    transcriber.set_service_url(url)
    try:
        transcribed_to_json = transcriber.recognize(audio=audio_file)
    except Exception as e:
        logger.error("Watson error; {0}".format(e))
        transcribed_to_json = []
    return transcribed_to_json


# def record_from_microphone():
#     r = recogniton.Recognizer()
#     with mic.Microphone() as source, Dinger():
#         print("Say something!")
#         audio = r.listen(source)
#     print("Ok - processing...")
#     return audio.get_wav_data()


class AutomaticSpeechRecognition(object):
    """
    The class AutomaticSpeechRecognition purpose is to convert speech to text.
    """

    def __init__(self):
        self.queue_manager = QueueManager(
            [self.__class__.__name__, "NaturalLanguageUnderstanding"]
        )

        logger.info(f"{self.__class__.__name__} ready")

    def callback(self, body, **_):
        """
        The function run by the queue manager when a message for this service reaches the front.

        :param body: a dictionary containing info required. This service expects to be the first run, so
                     only requires a "path_done" list to be inside.
        :param _:    Other callbacks may take more params. They should be ignored in this case.
        :return: None
        """
        logger.info(body)
        # body = callback_impl(body)

        logger.info(body["query"])
        body["path_done"].append(self.__class__.__name__)
        self.queue_manager.publish("NaturalLanguageUnderstanding", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    automatic_speech_recognition = AutomaticSpeechRecognition()
    automatic_speech_recognition.run()


if __name__ == "__main__":
    main()
