import os
from pathlib import Path

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
    __slots__ = ("rabbitmq", "directory", "ibmwatson")

    def __init__(self) -> None:
        self.rabbitmq = RabbitMQCreds()
        self.ibmwatson = IBMWatsonCreds()
        self.directory = Directories()

    def getenv(self, env_key: str) -> str:
        return os.getenv(env_key)
