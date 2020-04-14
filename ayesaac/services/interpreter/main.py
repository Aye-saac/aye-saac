
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager


class Interpreter(object):
    """
    The Interpreter class purpose is a simple comparison with what the vision part find out and what the user asked for.
    (Which object was found and not found)
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, 'NaturalLanguageGenerator'])
        self.memory = {}

    def filter_objects(self, body):
        return body['objects']

    def filter_texts(self, body):
        return body['texts']

    def callback(self, body, **_):
        data = None
        key = ''

        if 'objects' in body:
            key = 'objects'
            data = self.filter_objects(body)
            body['objects'] = data
        elif 'texts' in body:
            key = 'texts'
            data = self.filter_texts(body)
            body['texts'] = data

        if body['wait_package'] == 1:
            body['path_done'].append(self.__class__.__name__)
            del body['vision_path']
            pprint(body)
            # TODO: uncomment if you wanna test the NLG, it could be text, objects, objects + colour, objects + lateral position
            #self.queue_manager.publish('NaturalLanguageGenerator', body)
        else:
            if body['intern_token'] not in self.memory:
                self.memory[body['intern_token']] = {key: data}
            elif body['intern_token'] in self.memory and body['wait_package'] < len(self.memory[body['intern_token']]) - 1:
                self.memory[body['intern_token']][key] = data
            else:
                for key in self.memory[body['intern_token']]:
                    body[key] = self.memory[body['intern_token']][key]
                del self.memory[body['intern_token']][key]
                pprint(body)
                # TODO: uncomment if you wanna test the NLG
                #self.queue_manager.publish('NaturalLanguageGenerator', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    interpreter = Interpreter()
    interpreter.run()


if __name__ == "__main__":
    main()
