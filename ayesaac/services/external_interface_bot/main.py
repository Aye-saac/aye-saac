import json
from pathlib import Path

from ayesaac.queue_manager import QueueManager
from ayesaac.utils.logger import get_logger


logger = get_logger(__file__)


class ExternalInterface(object):
    """
    This service represents the end of the pipeline. All output is dumped here to be
    retrieved by the web server.
    """

    def __init__(self):
        project_root = Path(__file__).parent.parent.parent.parent
        self.output_dir = f"{project_root}/output"

        self.queue_manager = QueueManager([self.__class__.__name__])

        logger.info(f"{self.__class__.__name__} ready")

    def dump_output(self, body):
        # Get unique key
        key = body["uid"]

        file_name = f"{self.output_dir}/{key}.txt"

        with open(file_name, "w") as output_file:
            json.dump(body, output_file)

    def callback(self, body, **_):
        body["path_done"].append(self.__class__.__name__)

        self.dump_output(body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    external_interface = ExternalInterface()
    external_interface.run()


if __name__ == "__main__":
    main()
