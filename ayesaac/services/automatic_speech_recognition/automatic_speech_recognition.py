import os
import subprocess
from typing import Any, BinaryIO, cast

from ibm_cloud_sdk_core import DetailedResponse
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1

from ayesaac.services.common import ServiceBase
from ayesaac.utils.config import Config
from ayesaac.utils.logger import get_logger


config = Config()


logger = get_logger(__file__)


def get_wav_from_web_input(body: Any) -> bytes:
    """
    Voice files from the web come in ogg format.
    IBM takes files in wav format. Convert here.
    :param body: dict that passes between services
    :return: wav bytestream
    """
    voice_file = body["voice_file"]  # expected to be a path to a .ogg fil

    out_name = f"{voice_file[:-4]}.wav"

    # https://stackoverflow.com/a/60332477
    subprocess.call(["ffmpeg", "-i", f"{voice_file}", f"{out_name}"])

    with open(out_name, "rb") as f:
        wav = f.read()

    # TODO: Use proper tempfile library
    # cleanup temp files
    os.remove(out_name)
    os.remove(voice_file)

    return wav


class WatsonSpeechToText(object):
    def __init__(self) -> None:
        self.transcriber = self._get_transcriber()

    def __call__(self, audio_data: BinaryIO) -> str:
        transcribed_json = self._transcribe_to_json(audio_data)
        processed_transcript = self._process_transcribed_json(transcribed_json)

        return processed_transcript

    def _get_transcriber(self) -> SpeechToTextV1:
        url = config.ibmwatson.endpoint
        key = config.ibmwatson.api_key

        authenticator = IAMAuthenticator(key)
        transcriber = SpeechToTextV1(authenticator=authenticator)
        transcriber.set_service_url(url)

        return transcriber

    def _transcribe_to_json(self, audio_file: BinaryIO) -> DetailedResponse:
        try:
            return self.transcriber.recognize(audio=audio_file)
        except Exception as e:
            logger.error("(Watson): {0}".format(e))

    def _process_transcribed_json(self, transcribed_data: DetailedResponse) -> str:
        response = transcribed_data.get_result()
        assert response.ok

        try:
            transcript = response["results"][0]["alternatives"][0]["transcript"]

            return cast(str, transcript)

        except Exception as e:
            raise Exception(e)


class AutomaticSpeechRecognition(ServiceBase):
    """
    The class AutomaticSpeechRecognition purpose is to convert speech to text.
    """

    def __init__(self) -> None:
        super().__init__([self.__class__.__name__, "NaturalLanguageUnderstanding"])

        self.speech_to_text = WatsonSpeechToText()

        self.__post_init__()

    def callback(self, body, **_) -> None:
        """
        The function run by the queue manager when a message for this service reaches
        the front.
        """

        audio_data = get_wav_from_web_input(body)
        body["query"] = self.speech_to_text(audio_data)

        logger.info(body["query"])

        body = self._update_path_done(body)

        self.queue_manager.publish("NaturalLanguageUnderstanding", body)
