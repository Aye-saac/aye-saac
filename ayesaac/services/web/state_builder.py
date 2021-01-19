# A refactored user request state builder that hasn't been replaced yet.

import json
import os
import uuid
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, TypeVar, Union

import numpy as np
from flask import request
from PIL import Image

from ayesaac.queue_manager.crypter import encode

T = TypeVar("T")


@dataclass
class PictureState(object):
    data: bytes
    shape: np.ndarray
    source: str

    def as_dict(self) -> Dict[str, Any]:
        return {"data": self.data, "shape": self.shape, "source": self.source}


@dataclass
class State(object):
    uid: str
    run_as_webservice: bool
    responses: Any
    voice_file: Optional[str]
    pictures: List[PictureState]
    query: str = ""
    path_done: List[str] = []
    errors: List[str] = []

    def as_dict(self) -> Dict[Any, Any]:
        {
            "uid": self.uid,
            "responses": self.responses,
            "voice_file": self.voice_file,
            "pictures": [picture.as_dict() for picture in self.pictures],
            "path_done": self.path_done,
            "errors": self.errors,
            "query": self.query,
            "run_as_webservice": self.run_as_webservice,
        }


class ImageHandler(object):
    def __call__(self, stream: Any) -> np.ndarray:
        return self.handle_image_stream(stream)

    def handle_image_stream(self, stream: Any) -> np.ndarray:
        # Convert the file stream to a PIL Image
        image = Image.open(BytesIO(stream))

        # Downsize image
        downsized_image = self.downsize_image(image, 640)

        # Return image as numpy array
        return np.asarray(downsized_image)

    @staticmethod
    def downsize_image(image: Image, desired_width: int) -> Image:
        current_width = image.width
        current_height = image.height

        # Calculate ratio to scale the image
        ratio = current_width / desired_width

        new_size = (desired_width, int(current_height / ratio))

        return image.resize(new_size)


class AudioHandler(object):
    def __init__(self, uid: str) -> None:
        self._uid = uid

        self._file_ext = ".ogg"
        self._file_suffix = "_audio"

        self._audio_dir = "user_audio"

    def __call__(self, stream: Any) -> str:
        return self.handle_audio_stream(stream)

    def handle_audio_stream(self, stream: Any) -> str:
        """ Get the raw bytes from the audio. """

        # TODO: Is this in the form that will work for the system?
        # a hack a day keeps the doctor in fear

        dir_path = str(Path(__file__).parent / self._audio_dir)

        os.makedirs(dir_path, exist_ok=True)

        file_locus = str(Path(dir_path) / self._build_filename(self._uid))

        with open(file_locus, "wb") as f:
            f.write(stream)

        return file_locus

    def _build_filename(self, uid: str) -> str:
        return uid / self._file_suffix / self._file_ext


class RequestParser(object):
    __slots__ = ("text", "responses", "image", "audio")

    def __init__(self, uid: str) -> None:
        self.text = self._get_text()
        self.responses = self._get_responses()

        # Note: This only handles one image per request. If the request has more images,
        #       then it will probably fail.
        self.image = self._get_file("image", ImageHandler())
        self.audio = self._get_file("audio", AudioHandler(uid))

    @staticmethod
    def _get_file(
        file_name: str, callback: Callable[..., T]
    ) -> Union[T, Literal[False]]:
        file = request.files.get(file_name)

        if file:
            stream = file.read()
            return callback(stream)

        return False

    @staticmethod
    def _get_text() -> str:
        default_message = ""
        return request.form.get("message", default_message)

    @staticmethod
    def _get_responses() -> Any:
        default_response = "[]"
        responses = request.form.get("responses", default_response)
        return json.loads(responses)


class StateBuilder(object):
    """
    Get the data from the question and parse it in a form that should be
    usable by the rest of the system.

    Only handles FormData from client
    """

    def __init__(self, service_if_audio: str, service_if_text: str) -> None:
        self._uid = str(uuid.uuid4())

        self._service_if_audio = service_if_audio
        self._service_if_text = service_if_text

        self._request = RequestParser(self.uid)

    def __call__(self) -> Tuple[State, str]:

        first_service = (
            self._service_if_audio
            if self._is_message_audio()
            else self._service_if_text
        )

        audio_file = self._request.audio
        query = self._request.text

        state = State(
            uid=self._uid,
            responses=self._request.responses,
            run_as_webservice=True,
            pictures=[self._get_image()],
            voice_file=audio_file if self._is_message_audio() else None,
            query=query if not self._is_message_audio() else "",
        )

        return state, first_service

    def _get_image(self):
        image = self._request.image

        if image:
            return PictureState(
                data=encode(image),
                shape=np.shape(image),
                source="Web",
            )

    def _is_message_audio(self) -> bool:
        return True if self._request.audio else False
