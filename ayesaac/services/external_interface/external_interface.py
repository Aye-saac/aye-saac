import json
from pprint import pprint

from ayesaac.services.common import ServiceBase
from ayesaac.utils.config import Config
from ayesaac.utils.logger import get_logger


config = Config()


logger = get_logger(__file__)


class ExternalInterface(ServiceBase):
    def __init__(self) -> None:
        super().__init__([self.__class__.__name__])

        self.output_dir = config.directory.output

        self.__post_init__()

    def callback(self, body, **_):
        body["path_done"].append(self.__class__.__name__)
        pprint("attempting to dump body:")
        pprint("=====================")
        pprint(body)
        pprint("=====================")

        self.dump_output(body)

    def dump_output(self, body):
        # Get unique key
        key = body["uid"]

        file_name = f"{self.output_dir}/{key}.txt"

        with open(file_name, "w") as output_file:
            json.dump(body, output_file)
