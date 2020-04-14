# The head honcho. The big cheese. The main program entry point for the bot that sits with the server.
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from threading import Thread

from ayesaac.services.external_interface_bot import user_request
from ayesaac.services.external_interface_bot.user_request import UserRequest
from ayesaac.services_lib.queues.queue_manager import QueueManager

root_logger = logging.getLogger('ayesaac')
root_logger.setLevel(logging.DEBUG)

logfile = Path(__file__).parent.parent.parent.parent/'ayesaac'/'services_log'/'AppInterface.log'
file_handler = logging.FileHandler(logfile, mode='w')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s   [%(filename)s:%(lineno)d] - %(message)s')
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)


logger = logging.getLogger(__name__)

QM = QueueManager(["AppInterface", "AutomaticSpeechRecognition", "NaturalLanguageUnderstanding", 'TextToSpeech'])  # todo scope this sensibly instead of polluting the world
daemon_QM = QueueManager(["AppInterface"])


def get_first_service_name(data, request_content):
    if request_content.isAudio:
        first_service = "AutomaticSpeechRecognition"
        data['voice_file'] = request_content.message  # this recycling of .message is unhelpful
    elif request_content.message:
        first_service = "NaturalLanguageUnderstanding"
        data['query'] = request_content.message
    else:
        # total fallback; insert generic message
        first_service = "NaturalLanguageUnderstanding"
        message = "what can you see"
        error_log_msg = f'Bad message content; using fallback message: "{message}"'
        logging.warning(error_log_msg)
        data['query'] = message
        data['errors'].append(error_log_msg)
    return first_service


class LoopContextManager:
    """Helper class to safely release loop when destroyed"""

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def __enter__(self):
        return self.loop

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.close()


class AppInterface:
    """
    This class is a queue message producer and consumer.
    run and callback are required by our RabbitMQ queue system.

    Somewhat abomniably, this class starts its callback on a separate thread as a daemon at construction,
    while providing methods to submit work and wait on that daemon completing it.

    This can be run "synchronously" by calling `run_service_pipeline` to get a result returned directly,
    or asynchronously by `start_service_pipeline` and allowing for the caller to watch for the appropriate result.
    """
    def __init__(self, queue_manager=QM, test_run=False):
        # the following warning is redundant as this is no longer a web server, but should be kept in mind:

        # Warning: the init method will be called every time before the post() method
        # Don't use it to initialise or load files.
        # We will use kwargs to specify already initialised objects that are required to the bot
        # super(AppInterface, self).__init__(bot_name=BOT_NAME)
        self.test_run = test_run
        self.queue_manager = queue_manager
        self.daemon_queue_manager = daemon_QM
        # adds and removes as necessary
        self.result_cache = {}
        logger.info("Constructor called")
        self.app_thread = Thread(target=self.run, daemon=True)
        self.app_thread.start()

    def run_service_pipeline(self, request_content: UserRequest):
        """

        :param request_content: Dict of basic info provided by web client
        :return: Result of the pipeline, as dictated by the `callback` method on this class.
        """
        logger.info("Full pipeline requested.")
        # send...
        self.start_service_pipeline(request_content)

        # # ... and receive!
        # # https://stackoverflow.com/a/46750562
        key = request_content.id
        with LoopContextManager() as loop:
            result = loop.run_until_complete(asyncio.wait_for(asyncio.ensure_future(self.fetch_result(key)), timeout=30))

        return result

    async def fetch_result(self, uid):
        """
        Patiently checks for the completion of the service pipeline, as dictated by the `callback` method on this class.

        :return: the found result
        """
        found = False
        while not found:
            if uid in self.result_cache:
                found = True
            await asyncio.sleep(1)  # remove this for excitement!
        return self.result_cache.pop(uid)

    def start_service_pipeline(self, request_content: user_request):
        data = {"path_done": [], 'errors': [], "run_as_webservice": True}
        first_service = get_first_service_name(data, request_content)
        # start pipeline to get meanings and responses
        # pprint(data["web_request"])
        data["path_done"].append(self.__class__.__name__)
        data['uid'] = request_content.id
        if self.test_run or request_content.dryRun:
            # shortcut the pipeline, return this web request
            logging.info(f"""
            Fake run. Would have started {first_service} as the first service with the following data.
            Data dump:
            f{data}
            """)
            data["path_done"].append(self.__class__.__name__)
            data["response"] = "This was a dry run! Thank you :) "
            self.queue_manager.publish(self.__class__.__name__, data)
        else:
            # add picture
            logger.info('This is not a drill! Starting the real pipeline.')
            data['picture'] = {'data': request_content.image, 'shape': request_content.image, 'from': self.__class__.__name__}
            self.queue_manager.publish(first_service, data)
        logger.info('Pipeline started')

    def run(self):
        """
        Collect the results from the end of the pipeline for caching.
        :return:
        """
        logger.info("0 AppInterface now consuming from the queue.")
        self.daemon_queue_manager.start_consuming(self.__class__.__name__, self.callback)

    def callback(self, body, **_):
        """
        Callback called on the queue message being received.
        :param body: The output from the end of the queue of services. This includes everything, but specifically
            we are after the final output (e.g. a text response or tts sound file of that text).
        :param _:
        :return:
        """
        logger.info(f'Message Received: {body}')
        response = {'result': "BEEP BOOP I AM A ROBOT"} if self.test_run else body

        response["finish_time"] = str(datetime.now())
        key = body['uid']
        if key in self.result_cache:
            raise Exception(f"Key not unique! {key}")
        self.result_cache[key] = response

# no if __name__ == "__main__" section here; not a standalone service.
