
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager

import os
from random import choice

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

    def get_det(self, word):
        return str(word[1])+' ' if word[1] > 1 else 'a '

    def generate_text(self, words, context, obj_cnt):
        answer = choice(self.answers[context])
        if type(words) == str:
            return answer.replace('*', words, 1)
        elif len(words) > 1:
            tmp = ', '.join([self.get_det(w)+w[0] for w in words[:-1]]) + ' and '+self.get_det(words[-1])+words[-1][0]
            return answer.replace('*', tmp, 1)
        elif len(words):
            return answer.replace('*', str(words[0][1])+' ' if words[0][1] > 1 else ''+words[0][0], 1)
        return answer

    def callback(self, body, **_):
        pprint(body)

        objects = None
        context = None
        if body['intents']['intent']['name'] == 'identify':
            objects = []
            for o in body['objects']:
                if o['name'] != 'person':
                    # objects.append(o['name']+o['lateral_position'])
                    objects.append(o['name'])
            objects = list(set([(o, objects.count(o)) for o in objects]))
            obj_cnt = sum(n for _, n in objects)
            context = self.description_types[obj_cnt if obj_cnt < 2 else 2]
        elif body['intents']['intent']['name'] == 'recognise':
            objects = []
            for o in body['objects']:
                for p in body['intents']['entities']:
                    if o['name'] == p['value']:
                        # objects.append(o['name']+o['lateral_position'])
                        objects.append(o['name'])
            objects = list(set([(o, objects.count(o)) for o in objects]))
            obj_cnt = sum(n for _, n in objects)
            context = ('POSITIVE' if obj_cnt > 0 else 'NEGATIVE') + '_ANSWER_' + ('P' if obj_cnt > 1 else 'S')
            if not obj_cnt:
                objects = [(p['value'], 1) for p in body['intents']['entities']]
                obj_cnt = sum(n for _, n in objects)
        elif body['intents']['intent']['name'] == 'read_text':
            objects = ' '.join(' '.join(t) for t in body['texts'])
            print(objects)
            obj_cnt = 1 if len(objects) > 0 else 0
            context = 'READ_TEXT_'+('POSITIVE' if obj_cnt > 0 else 'NEGATIVE')
        elif body['intents']['intent']['name'] == 'detect_colour':
            pass
        elif body.get('objects'):
            # Creates list of object detected in the scene
            objects = [o['name']+o['lateral_position'] for o in body['objects']]
            objects = list(set([(o, objects.count(o)) for o in objects]))
            obj_cnt = sum(n for _, n in objects)
            context = self.description_types[obj_cnt if obj_cnt < 2 else 2]
        print(objects)
        print(context)
        if objects != None and context != None:
            response = self.generate_text(objects, context, obj_cnt)
        else:
            response = 'I didn\'t understand the question, could you repeat please.'

        body["response"] = response
        pprint(body['response'])
        body["path_done"].append(self.__class__.__name__)

        self.queue_manager.publish("TextToSpeech", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_generator = NaturalLanguageGenerator()
    natural_language_generator.run()


if __name__ == "__main__":
    main()
