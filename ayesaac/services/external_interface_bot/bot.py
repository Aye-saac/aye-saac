# The head honcho. The big cheese. The main program entry point for the bot that sits with Alana.

import logging
from argparse import ArgumentParser

import os
from flask import Flask, request
from flask_restful import Api
from utils import log
from utils.abstract_classes import Bot
from utils.dict_query import DictQuery
from datetime import datetime

from ayesaac.services_lib.queues.queue_manager import QueueManager
from pprint import pprint

app = Flask(__name__)
api = Api(app)
BOT_NAME = "ayesaac"
VERSION = log.get_short_git_version()
BRANCH = log.get_git_branch()

logger = logging.getLogger(__name__)

parser = ArgumentParser()
parser.add_argument('-p', "--port", type=int, default=5130)  # todo set from environment to ease dockerisation
parser.add_argument('-l', '--logfile', type=str, default='logs/' + BOT_NAME + '.log')
parser.add_argument('-cv', '--console-verbosity', default='info', help='Console logging verbosity')
parser.add_argument('-fv', '--file-verbosity', default='debug', help='File logging verbosity')

QM = QueueManager(["AutomaticSpeechRecognition", "NaturalLanguageUnderstanding", 'TextToSpeech'])  # todo scope this sensibly instead of polluting the world
result_store = {}


class UidMaker:
    uid_counter = 0

    def generate_uid(self):
        """
        UIDs are expected to not last beyond server lifetime.
        todo handle large numbers
        :return: a uid (integer)
        """
        self.uid_counter = self.uid_counter + 1
        return self.uid_counter


uids = UidMaker()

class WebServer(Bot):
    """
    This class is both a webserver and a queue message producer and consumer.
    get and post are required by flask to put up the web server,
    run and callback are required by our RabbitMQ queue system.
    """
    def __init__(self, **kwargs):
        # Warning: the init method will be called every time before the post() method
        # Don't use it to initialise or load files.
        # We will use kwargs to specify already initialised objects that are required to the bot
        super(WebServer, self).__init__(bot_name=BOT_NAME)
        self.queue_manager = QM
        self.result_store = result_store
        self.uid_maker = uids

    def get(self):
        if self.result_store:
            return self.result_store
        else:
            return None  # todo return the correct object in this case

    def post(self):
        # This method will be executed for every POST request received by the server on the
        # "/" endpoint (see below 'add_resource')

        # We assume that the body of the incoming request is formatted as JSON (i.e., its Content-Type is JSON)
        # We parse the JSON content and we obtain a dictionary object
        request_data = request.get_json(force=True)
        # We wrap the resulting dictionary in a custom object that allows data access via dot-notation
        request_data = DictQuery(request_data)

        request_content = self.extract_request_content(request_data)

        # initialise service pipeline with a UID to match the results in the GET
        uid = self.generate_and_store_UID()
        request_content['uid'] = uid

        self.start_service_pipeline(request_content)

        return {'uid': uid}

    def generate_and_store_UID(self):
        """
        1. Create a UID
        2. Create an empty entry in the results cache (dictionary) to be filled later
        :return: the new UID
        """
        uid = self.uid_maker.generate_uid()
        self.result_store[uid] = ""  # todo work out if empty string is a problem
        return uid

    def start_service_pipeline(self, request_content):
        data = {"path_done": []}
        if 'text_question' in request_content and request_content['text_question']:
            first_service = "NaturalLanguageUnderstanding"
            data['query'] = request_content['text_question']
        elif 'voice' in request_content and request_content['voice']:
            first_service = "AutomaticSpeechRecognition"
            data['voice_file'] = request_content['voice']
        # start pipeline to get meanings and responses
        # pprint(data["web_request"])
        data["path_done"].append(self.__class__.__name__)

        # todo fake_run shouldn't be in here
        fake_run = True
        if fake_run:  # todo add fake_run variable for testing
            logging.info(f"""
            Fake run. Would have started {first_service} as the first service with the following data.
            Data dump:
            f{data}
            """)
        else:
            self.queue_manager.publish(first_service, data)
        logging.info('Pipeline started')

    def run(self):
        """
        Collect the results from the end of the pipeline for caching.
        :return:
        """
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)

    def callback(self, body, **_):
        """
        Callback called on the queue message being received.
        :param body: The output from the end of the queue of services. This inludes everything, but specifically
            we are after the final output (e.g. a sound file).
        :param _:
        :return:
        """
        # NLG
        # the 'result' member is intended as the actual response of the bot
        # todo affirm test switch properly
        self.response.result = "BEEP BOOP I AM AUDIO OUTPUT"  # #nlg.generate_response(intention)
        # we store in the dictionary 'bot_params' the current time. Remember that this information will be stored
        # in the database only if the bot is selected
        self.response.bot_params["time"] = str(datetime.now())
        # # The response generated by the bot is always considered as a list (we allow a bot to generate multiple response
        # # objects for the same turn). Here we create a singleton list with the response in JSON format
        # return [self.response.toJSON()]
        self.result_store = self.response.toJSON()

    def extract_request_content(self, request_data):
        """
        Request data has data with encodings to deal with. Deal with them here.
        :param request_data:
        :return:
        """
        # todo catch nonpresent data failures
        request_content = {#'img': Image.open(BytesIO(request_data.image)),  # todo read in images
                           #'voice': Image.open(BytesIO(request_data.voice)), # todo make audio file
                           'text_question': request_data.text_question,
                           'history': request_data.history
                           }

        return request_content

# @app.route('/')
# def test_porting():
#     return "Welcome, Connectomatron :)"


if __name__ == "__main__":
    args = parser.parse_args()

    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    log.set_logger_params(BOT_NAME + '-' + BRANCH, logfile=args.logfile,
                          file_level=args.file_verbosity, console_level=args.console_verbosity)

    api.add_resource(WebServer, "/")
    logger.info(f"Launching app on port {args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=True)
