from typing import TypeVar

from .service_base import ServiceBase


T = TypeVar("T", bound=ServiceBase)


def run_service_wrapper(Service: T) -> None:
    service = Service()
    service.run()
