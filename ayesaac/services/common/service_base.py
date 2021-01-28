from typing import Any, List, TypeVar

from ayesaac.utils.logger import get_logger

from .queue_manager import QueueManager


T = TypeVar("T")

logger = get_logger(__file__)


class ServiceBase(object):
    def __init__(self, queue_names: List[str]) -> None:
        if self.__class__.__name__ not in queue_names:
            raise AssertionError(f"{self.__class__.__name__} is not in the queue list")

        self.queue_manager = QueueManager(queue_names)

    def __post_init__(self) -> None:
        logger.info(f"{self.__class__.__name__} ready")

    def callback(self, body: Any, **_) -> None:
        raise NotImplementedError

    def run(self) -> None:
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)

    def _update_path_done(self, body: T) -> T:
        return body["path_done"].append(self.__class__.__name__)
