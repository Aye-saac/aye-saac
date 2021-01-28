"""
crypter.py
This file contain encode and decode method which is allow to send images through queues.
The image is represented as a numpy array and it is convert in base64 byte string.
"""


import base64

import numpy as np


def decode(image: bytes, shape: np.array, dtype=np.uint8) -> np.array:
    """
    Transform a byte string back to a numpy array
    :param image: byte string
    :param shape: original shape
    :param type: data type
    :return: np.array
    """

    img = base64.decodebytes(image.encode())
    img = np.frombuffer(img, dtype=dtype)
    return np.reshape(img, shape)


def encode(raw_image: np.array):
    """
    Transform a numpy array to a string byte
    :param raw_image: numpy array
    :return:
    """

    encoded_image = base64.b64encode(
        np.copy(raw_image, order="C").astype(np.uint8)
    ).decode("utf-8")

    return encoded_image
