
from pprint import pprint

from services_lib.queues.queue_manager import QueueManager

import os
from random import choice
from gtts import gTTS
from playsound import playsound


class NaturalLanguageGenerator(object):
    """
    The class NaturalLanguageGenerator purpose is to translate the results obtain to a nicely phrase.
    """
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "TextToSpeech"])
        self.answers = {}
        self.description_types = ['DESCRIPTION_NOTHING', 'DESCRIPTION_ANSWER_S','DESCRIPTION_ANSWER_P']
        self.build_generator()
        print('Answers found:')
        pprint(self.answers)

    def build_generator(self):
        folder_path = 'services/natural_language_generator/answers/'
        for _, _, files in os.walk(folder_path):
            for name in files:
                with open(folder_path+name) as f:
                    self.answers[name] = [line.strip() for line in f]

    def generate_text(self, words, context):
        # answer = choice(self.answers[context+'_P']) if type(words) == list else choice(answers[context+'_S'])
        answer = choice(self.answers[context])
        if type(words) == list:
            return answer.replace('*', 'a '+', a '.join(words[:-1])+' and a '+words[-1], 1)
        else:
            return answer.replace('*', words, 1)

    def callback(self, body, **_):
        pprint(body)


        ## Previous work
        # response = 'I found'
        # for from_ in body['results']:
        #     for obj in body['results'][from_]:
        #         if body['results'][from_][obj] > 0:
        #             response += ' ' + str(body['results'][from_][obj]) + ' ' + obj + ' from the ' + from_ + ','

        # if len(response) == 7:
        #     response += ' nothing.'
        # else:
        #     response = response[:-1] + '.'

        # Creates list of object detected in the scene
        objects = [o['name'] for o in body['objects']]
        obj_cnt = len(objects)
        response = self.generate_text(objects, self.description_types[obj_cnt if obj_cnt < 2 else 2])
        # if obj_cnt > 1:
        #     response = self.generate_text(objects, 'DESCRIPTION_ANSWER_P')
        # elif obj_cnt > 0:
        #     response = self.generate_text(objects, 'DESCRIPTION_ANSWER_S')
        # else:
        #     response = self.generate_text(objects, 'DESCRIPTION_NOTHING')

        body["response"] = response
        pprint(body['response'])
        body["path_done"].append(self.__class__.__name__)

        del body["asking"], body["objects"], body["path"], body["query"], body["results"]
        self.queue_manager.publish("TextToSpeech", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_generator = NaturalLanguageGenerator()
    natural_language_generator.run()


if __name__ == "__main__":
    main()
