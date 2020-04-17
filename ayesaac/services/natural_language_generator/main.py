from pathlib import Path
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager

import os
from random import choice


class NaturalLanguageGenerator(object):
    """
    The class NaturalLanguageGenerator purpose is to translate the results obtain to a nicely phrase.
    """
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__,
                                           "ExternalInterface"])
        self.answers = {}
        self.description_types = ['DESCRIPTION_NOTHING', 'DESCRIPTION_ANSWER_S','DESCRIPTION_ANSWER_P']
        self.build_generator()
        print('Answers found:')
        pprint(self.answers)

    def build_generator(self):
        project_root = Path(__file__).parent.parent.parent.parent  # aye-saac
        folder_path = project_root/'ayesaac'/'services'/'natural_language_generator'/'answers'
        for _, _, files in os.walk(folder_path):
            for name in files:
                with open(str(folder_path/name)) as f:
                    self.answers[name] = [line.strip() for line in f]

    def get_det(self, word):
        return str(word[1])+' ' if word[1] > 1 else 'a '

    def generate_text(self, words, context, obj_cnt):
        answer = choice(self.answers[context])
        if len(words) > 1:
            tmp = ', '.join([self.get_det(w)+w[0] for w in words[:-1]]) + ' and '+self.get_det(words[-1])+words[-1][0]
            return answer.replace('*', tmp, 1)
        elif len(words):
            return answer.replace('*', str(words[0][1])+' ' if words[0][1] > 1 else ''+words[0][0], 1)
        return answer

    def callback(self, body, **_):
        pprint(body)

        # Creates list of object detected in the scene
        objects = [o['name']+o['lateral_position'] if 'lateral_position' in o else o['name'] for o in body['objects']]
        objects = list(set([(o, objects.count(o)) for o in objects]))
        print(objects)
        obj_cnt = sum(n for _, n in objects)
        response = self.generate_text(objects, self.description_types[obj_cnt if obj_cnt < 2 else 2], obj_cnt)

        body["response"] = response
        pprint(body['response'])
        body["path_done"].append(self.__class__.__name__)

        del body["objects"]
        self.queue_manager.publish("ExternalInterface", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_generator = NaturalLanguageGenerator()
    natural_language_generator.run()


if __name__ == "__main__":
    main()
