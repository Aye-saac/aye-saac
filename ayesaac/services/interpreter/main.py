
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager


class Interpreter(object):
    """
    The Interpreter class purpose is a simple comparison with what the vision part find out and what the user asked for.
    (Which object was found and not found)
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, 'NaturalLanguageGenerator'])

    def callback(self, body, **_):
        pprint(body)

        if 'objects' in body:
            results = {}
            for object_found in body['objects']:
                results[object_found['from']] = {}

            for object_found in body['objects']:
                if (object_found['name'] in body['asking'] or '*' in body['asking']) and object_found['confidence'] > 0.5:
                    if not object_found['name'] in results[object_found['from']]:
                        results[object_found['from']][object_found['name']] = 1
                    else:
                        results[object_found['from']][object_found['name']] += 1

            body["results"] = results
            pprint(body['results'])
        body['path_done'].append(self.__class__.__name__)
        del body['vision_path']
        # TODO: uncomment if you wanna test the NLG, it could be text, objects, objects + color, objects + lateral position
        #self.queue_manager.publish('NaturalLanguageGenerator', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    interpreter = Interpreter()
    interpreter.run()


if __name__ == "__main__":
    main()
