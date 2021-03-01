import os
import time

from flask import Flask, url_for
from flask_cors import CORS

from ayesaac.services.common import QueueManager
from ayesaac.utils.config import Config

from .user_request import UserRequest


config = Config()

# Create Flask app
app = Flask(__name__)
app.config["CORS_HEADERS"] = "Location"

CORS(
    app,
    origins=config.endpoint_service.cors_origins,
    expose_headers=["Location"],
)


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello world"


@app.route("/submit", methods=["POST"])
def submit():
    service_if_audio = "AutomaticSpeechRecognition"
    service_if_text = "NaturalLanguageUnderstanding"

    # Parse user request
    user_request = UserRequest(
        service_if_audio=service_if_audio, service_if_text=service_if_text
    )

    # Create queue for Ayesaac and send it
    ayesaac_queue_manager = QueueManager([user_request.first_service])
    ayesaac_queue_manager.publish(user_request.first_service, user_request.body)

    status_url = url_for("submit_status", task_id=user_request.uid)

    return (
        status_url,
        202,
        {"Location": status_url},
    )


@app.route("/status/<task_id>")
def submit_status(task_id):

    file_path = f"output/{task_id}.txt"

    attempt_counter = 0
    attempt_limit = 15

    while not os.path.exists(file_path):
        time.sleep(2)
        attempt_counter += 1
        if attempt_counter > attempt_limit:
            break

    file_exists = os.path.isfile(file_path)


    # Return if its not there
    if file_exists is not True:
        return "not found", 404

    # Get data from file
    with open(file_path, "r") as f:
        data = f.read()

    # Delete file
    # os.remove(file_path)

    # Return response
    return data, 200
