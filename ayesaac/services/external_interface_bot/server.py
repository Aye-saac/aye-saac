from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from ayesaac.services.external_interface_bot.user_request import UserRequest
from ayesaac.services.external_interface_bot.app_interface import AppInterface
import logging
from pathlib import Path

# Logging spam. Sadly this doesn't seem to apply to this file, but the flask info is still useful.
top_logger = logging.getLogger()
# Copied from the logging cookbook
# create file handler which logs even debug messages
logdir = Path(__file__).parent.parent.parent.parent/'ayesaac'/'services_log'
fh = logging.FileHandler(str(logdir/'spam.log'))
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s %(processName) %(name)s %(levelname)s: %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
top_logger.addHandler(fh)
top_logger.addHandler(ch)

# setup flask
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, origins=["localhost", "https://ayesaac.netlify.com", "http://127.0.0.1:3000"], allow_headers="Content-Type")

# capture flask errors
for handler in top_logger.handlers:
    app.logger.addHandler(handler)

logger = app.logger

app_interface = AppInterface()


class UserResponse:
    """ Package the data up from the system to be sent back to the user.
    
        TODO: Consider if this is even needed? If the TTS is done on the
              client-side, then only the JSON response from the system needs to
              be returned and this entire class is just OTT. But it's just for
              consistency sake? YAGNI, so remove if it is unneeded.
    """
    
    def __init__(self, response):
        self.response = response

# left as a dumb is_alive
@app.route("/", methods=["GET"])
def hello_world():
    logger.info("GET request received.")
    return "Hello world"


@app.route("/submit", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type"])
def submit_data():
    logger.info('POST request received. Beginning processing...')
    # Create a class containing the information needed to work
    user_request = UserRequest()

    # send to the services
    # todo add a way of matching submissions here to future responses, e.g. a UID or cookie id
    data = app_interface.run_service_pipeline(user_request)
    assert data['response']
    return jsonify(data=data)