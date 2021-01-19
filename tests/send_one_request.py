"""
send_one_request.py
Usage:
    python3 send_one_request.py

Start the workflow by sending a package to the first modules of the chain: AutomaticSpeechRecognition
Will be replace in the future by an Flask API for example
"""

from sys import argv

from ayesaac.services_lib.queues.queue_manager import QueueManager

if __name__ == '__main__':
    data = {"path_done": []}
    queue_manager = QueueManager(["AutomaticSpeechRecognition"])
    if len(argv) == 2:
        query = argv[1]
        print("Sending: " + query)
        data['query'] = query
    else:
        print("Sending")
    queue_manager.publish("AutomaticSpeechRecognition", data)
    print("Send")
    print()
