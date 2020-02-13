import random


def generate_response(intention):
    """
    Make something up that impresses people that talk to us!
    :param intention: An indication of what the user wants us to do, as parsed by the NLU unit.
    :return:
    """
    try:
        # Do something interesting with the intention here!
        raise(Exception("Unable to hold a conversation!"))

    except(Exception):
        # Handle fallback here
        nlg = NaturalLanguageGenerator()
        return random.choice(nlg.off_guard)


class NaturalLanguageGenerator:
    def __init__(self):
        self.off_guard = [
            "I know what you did.",
            "Sorry about your car.",
            "Hmm? I'm not sure that I'm the one you want to be talking to right now."
        ]