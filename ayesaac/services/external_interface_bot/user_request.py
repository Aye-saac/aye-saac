from flask import request
from PIL import Image
from io import BytesIO


class UserRequest:
    """ Get the data from the question and parse it in a form that should be
        usable by the rest of the system.
    """

    def __init__(self):
        self.image = self.__parse_image()
        text = self.__parse_message()
        audio = self.__parse_audio()

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
        return request.form.get("message", "")

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

    def __parse_image(self):
        def handle_image_stream(stream):
            # Convert the file stream to a PIL Image and return
            return Image.open(BytesIO(stream))

        return self.__parse_file("image", handle_image_stream)
