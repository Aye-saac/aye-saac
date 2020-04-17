import os

from flask import Flask, url_for

from ayesaac.web.user_request import UserRequest

from ayesaac.services_lib.queues.queue_manager import QueueManager


# Create Flask app
app = Flask(__name__)

state = {}


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

    return (
        "",
        202,
        {"Location": url_for("submit_status", task_id=user_request.uid)},
    )


@app.route("/status/<task_id>")
def submit_status(task_id):

    print(os.getcwd())

    file_path = f"output/{task_id}.txt"

    file_exists = os.path.isfile(file_path)

    # Return if its not there
    if file_exists is not True:
        return "PENDING", 202

    # Get data from file
    with open(file_path, "r") as file:
        data = file.read()

    # Delete file
    os.remove(file_path)

    # Return response
    return data, 200
