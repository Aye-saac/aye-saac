from ayesaac.services.common import run_service_wrapper

from .automatic_speech_recognition import AutomaticSpeechRecognition


if __name__ == "__main__":
    run_service_wrapper(AutomaticSpeechRecognition)
