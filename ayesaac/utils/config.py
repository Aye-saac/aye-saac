import os
from pathlib import Path
from typing import List

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


class RabbitMQCreds(object):
    @property
    def host(self) -> str:
        return os.getenv("RABBITMQ_HOST")

    @property
    def username(self) -> str:
        return os.getenv("RABBITMQ_USERNAME")

    @property
    def password(self) -> str:
        return os.getenv("RABBITMQ_PASSWORD")


class IBMWatsonCreds(object):
    @property
    def api_key(self) -> str:
        return os.getenv("IBM_API_KEY")

    @property
    def endpoint(self) -> str:
        return os.getenv("IBM_WATSON_ENDPOINT")


class EndpointService(object):
    def __init__(self, delimiter: str) -> None:
        self._delimiter = delimiter

    @property
    def cors_origins(self) -> List[str]:
        url_as_string = os.getenv("ENDPOINT_DOMAINS")
        return url_as_string.split(self._delimiter)


class Directories(object):
    @property
    def root(self) -> Path:
        return Path().absolute()

    @property
    def data(self) -> Path:
        return self.root.joinpath("data")

    @property
    def output(self) -> Path:
        return self.root.joinpath("output")


class Config(object):
    __slots__ = ("rabbitmq", "directory", "ibmwatson", "endpoint_service")

    def __init__(self) -> None:
        self.rabbitmq = RabbitMQCreds()
        self.ibmwatson = IBMWatsonCreds()
        self.directory = Directories()
        self.endpoint_service = EndpointService(" ")

    def getenv(self, env_key: str) -> str:
        return os.getenv(env_key)
