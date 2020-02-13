from utils.dict_query import DictQuery


def extract_intent(request_data: DictQuery):
    """
    Get an intent out of the user text the bot received.

    :param request_data: The full json received with the POST request. User text is under the key 'question'.
    :return: One of a set of intents. Enum, maybe?
    """
    intent = True  # sentence exists, probably
    return intent
