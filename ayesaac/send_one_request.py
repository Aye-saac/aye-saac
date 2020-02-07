"""
send_one_request.py
Usage:
    python3 send_one_request.py

Start the workflow by sending a package to the first modules of the chain: AutomaticSpeechRecognition
Will be replace in the future by an Flask API for example
"""

from lib.queues.queue_manager import QueueManager

if __name__ == '__main__':
    queue_manager = QueueManager(["AutomaticSpeechRecognition"])
    data = {"path_done": []}
    print("Sending")
    queue_manager.publish("AutomaticSpeechRecognition", data)
    print("Send")
    print()
