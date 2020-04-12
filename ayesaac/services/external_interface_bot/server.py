from flask import Flask, request

from ayesaac.services.external_interface_bot.user_request import UserRequest

app = Flask(__name__)


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
