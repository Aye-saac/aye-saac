import json
import os
import uuid
from pathlib import Path

from flask import request
from PIL import Image
from io import BytesIO
import numpy as np

from ayesaac.services_lib.images.crypter import encode


class UserRequest:
    """ Get the data from the question and parse it in a form that should be
        usable by the rest of the system.
        
        Only handles FormData from client
    """

    def __init__(self, service_if_audio, service_if_text):
        self.service_if_audio = service_if_audio
        self.service_if_text = service_if_text

        self.first_service = self.service_if_text

        # Create new uid
        self.uid = str(uuid.uuid4())

        # Create body
        self.body = {
            "uid": self.uid,
            "path_done": [],
            "errors": [],
            "run_as_webservice": True,
            "query": "",
        }

        # Add image to body
        self.__get_image()

        # Add message and update first_service
        self.__get_message()

        # Add responses to body
        self.__get_responses()

    @staticmethod
    def __parse_text():
        default_message = ""
        return request.form.get("message", default_message)

    @staticmethod
    def __parse_responses():
        default_response = "[]"
        responses = request.form.get("responses", default_response)
        return json.loads(responses)

    @staticmethod
    def __parse_file(file_name: str, func):
        file = request.files.get(file_name)

        if file:
            stream = file.read()
            return func(stream)

        return False

    @staticmethod
    def __downsize_image(image: Image, desired_width: int) -> Image:
        current_width = image.width
        current_height = image.height

        # Calculate ratio to scale the image
        ratio = current_width / desired_width

        new_size: tuple = (desired_width, int(current_height / ratio))

        return image.resize(new_size)

    def __parse_audio(self):
        filename = f'{self.body["uid"]}_audio.ogg'

        def handle_audio_stream(stream):
            # Get the raw bytes from the audio
            # TODO: Is this in the form that will work for the system?
            # a hack a day keeps the doctor in fear
            dir_path = str(Path(__file__).parent / 'user_audio')
            os.makedirs(dir_path, exist_ok=True)
            file_locus = str(Path(dir_path)/filename)
            with open(file_locus, 'wb') as f:  # writing bytes
                f.write(stream)
            return file_locus

        # Return parsed audio
        return self.__parse_file("audio", handle_audio_stream)

    def __parse_image(self) -> np.ndarray:
        def handle_image_stream(stream):
            # Convert the file stream to a PIL Image
            image = Image.open(BytesIO(stream))

            # Downsize image
            downsized_image = self.__downsize_image(image, 640)

            # Return image as numpy array
            return np.asarray(downsized_image)

        # Return parsed image
        return self.__parse_file("image", handle_image_stream)

    def __get_image(self):
        image = self.__parse_image()

        self.body["pictures"] = [
            {"data": encode(image), "shape": np.shape(image), "from": "Web",}
        ]

    def __get_message(self):
        text = self.__parse_text()
        audio = self.__parse_audio()

        if audio:
            self.body["voice_file"] = audio
            self.is_audio = True
            self.first_service = self.service_if_audio

        elif text:
            self.body["query"] = text
            self.is_audio = False
            self.first_service = self.service_if_text

    def __get_responses(self):
        self.body["responses"] = self.__parse_responses()
