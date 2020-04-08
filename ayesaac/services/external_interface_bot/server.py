from flask import Flask, request
from PIL import Image
from io import BytesIO

app = Flask(__name__)


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
        
        
class UserResponse:
    """ Package the data up from the system to be sent back to the user.
    
        TODO: Consider if this is even needed? If the TTS is done on the
              client-side, then only the JSON response from the system needs to
              be returned and this entire class is just OTT. But it's just for
              consistency sake? YAGNI, so remove if it is unneeded.
    """
    
    def __init__(self, response):
        self.response = response
        

# TODO: remove this as its not longer needed
@app.route("/")
def hello_world():
    return "Hello world"


@app.route("/submit", methods=["POST"])
def submit_data():
    # Create a class containing the information needed to work
    user_request = UserRequest()
    
    # TODO: Print statements can be removed.
    print(user_request.image)
    print(user_request.message)
    print(user_request.isAudio)
    
    # TODO: This should probably be the actual response
    return "", 204
