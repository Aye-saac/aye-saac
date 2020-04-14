from flask import request
from PIL import Image
from io import BytesIO
import numpy as np


class UserRequest:
    """ Get the data from the question and parse it in a form that should be
        usable by the rest of the system.

        Claims to handle input in JSON and formData.
    """

    def __init__(self):
        self.image: np.ndarray = self.__parse_image()
        self.id: str = self.__parse_request_id()
        text = self.__parse_message()
        audio = self.__parse_audio()
        test = self.__parse_test()

        # indicates that following data may be faked
        self.dryRun = True if test else False

        if audio:
            self.message = audio
            self.isAudio = True
        elif text:
            self.message = text
            self.isAudio = False
        else:
            raise Exception("There is neither a text nor audio input in the "
                            "request")

    @staticmethod
    def __parse_message():
        in_text = request.form.get("message", "")
        return in_text if in_text else request.json['message'] if request.json else None

    @staticmethod
    def __parse_request_id():
        """ Get the request ID (a UUID generated from the front end)
        """
        return request.form.get("request_id", "no_id")

    @staticmethod
    def __parse_test():
        if request.json:
            return bool(request.json['test'])
        elif request.form:
            return bool(request.form.get("test", ""))
        else:
            # no data supplied? smells fishy!
            raise Exception("No data supplied by client")

    @staticmethod
    def __parse_file(file_name: str, func):
        file = request.files.get(file_name)

        if file:
            stream = file.read()
            return func(stream)

        return False

    def __parse_audio(self):
        def handle_audio_stream(stream):
            # Get the raw bytes from the audio
            # TODO: Is this in the form that will work for the system?
            return BytesIO(stream)

        return self.__parse_file("audio", handle_audio_stream)

    def __parse_image(self) -> np.ndarray:
        def handle_image_stream(stream):
            # Convert the file stream to a PIL Image and return
            image = Image.open(BytesIO(stream))
            downsized_image = self.__downsize_image(image, 640)
            return np.asarray(downsized_image)

        return self.__parse_file("image", handle_image_stream)
    
    @staticmethod
    def __downsize_image(image: Image, desired_width: int) -> Image:
        current_width = image.width
        current_height = image.height
        
        # Calculate ratio to scale the image
        ratio = current_width / desired_width
        
        new_size: tuple = (desired_width, int(current_height / ratio))
        
        return image.resize(new_size)
