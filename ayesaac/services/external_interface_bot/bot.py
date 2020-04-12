# The head honcho. The big cheese. The main program entry point for the bot that sits with Alana.
import asyncio
import logging
from datetime import datetime

from ayesaac.services_lib.queues.queue_manager import QueueManager


logger = logging.getLogger(__name__)

QM = QueueManager(["AppInterface", "AutomaticSpeechRecognition", "NaturalLanguageUnderstanding", 'TextToSpeech'])  # todo scope this sensibly instead of polluting the world


class AppInterface:
    """
    This class is a queue message producer and consumer.
    run and callback are required by our RabbitMQ queue system.

    This can be run synchronously by calling `run_service_pipeline` to get a result returned directly,
    or asynchronously by `start_service_pipeline` and watching for the appropriate result property from the caller.
    """
    def __init__(self, queue_manager=QM, test_run=False):
        # the following warning is redundant as this is no longer a web server, but should be kept in mind:

        # Warning: the init method will be called every time before the post() method
        # Don't use it to initialise or load files.
        # We will use kwargs to specify already initialised objects that are required to the bot
        # super(AppInterface, self).__init__(bot_name=BOT_NAME)
        self.test_run = test_run
        self.queue_manager = queue_manager
        # self.result_store = ...  # todo create a more persistent result store
        self.single_result_cache = {}

    # def get(self):
    #     if self.result_store:
    #         return self.result_store
    #     else:
    #         return None  # todo return the correct object in this case

    # def post(self):
    #     # This method will be executed for every POST request received by the server on the
    #     # "/" endpoint (see below 'add_resource')
    #
    #     # We assume that the body of the incoming request is formatted as JSON (i.e., its Content-Type is JSON)
    #     # We parse the JSON content and we obtain a dictionary object
    #     request_data = request.get_json(force=True)
    #     # We wrap the resulting dictionary in a custom object that allows data access via dot-notation
    #     request_data = DictQuery(request_data)
    #
    #     request_content = self.extract_request_content(request_data)
    #
    #     # initialise service pipeline with a UID to match the results in the GET
    #     uid = self.generate_and_store_UID()
    #     request_content['uid'] = uid
    #
    #     self.start_service_pipeline(request_content)
    #
    #     return {'uid': uid}

    # def generate_and_store_UID(self):
    #     """
    #     1. Create a UID
    #     2. Create an empty entry in the results cache (dictionary) to be filled later
    #     :return: the new UID
    #     """
    #     uid = self.uid_maker.generate_uid()
    #     self.result_store[uid] = ""  # todo work out if empty string is a problem
    #     return uid

    def run_service_pipeline(self, request_content):
        """

        :param request_content: Dict of basic info provided by web client
        :return: Result of the pipeline, as dictated by the `callback` method on this class.
        """

        # send...
        self.start_service_pipeline(self, request_content)

        # ... and receive!
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.fetch_result())
        loop.close()
        return result

    async def fetch_result(self):
        """
        Patiently checks for the completion of the service pipeline, as dictated by the `callback` method on this class.

        :return: the found result
        """
        found = False
        while not found:
            if self.single_result_cache:
                found = True
            await asyncio.sleep(1)  # remove this for excitement!
        return self.single_result_cache

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

        if self.test_run:
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
        self.queue_manager.start_consuming("AppInterface", self.callback)

    def callback(self, body, **_):
        """
        Callback called on the queue message being received.
        :param body: The output from the end of the queue of services. This includes everything, but specifically
            we are after the final output (e.g. a text response or tts sound file of that text).
        :param _:
        :return:
        """

        response = {'result': "BEEP BOOP I AM A ROBOT"} if self.test_run else body

        response["finish_time"] = str(datetime.now())

        self.single_result_cache = response

# no if __name__ == "__main__" section here; not a standalone service.
