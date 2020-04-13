import json

import requests
from pathlib import Path
# from utils.address import address


# data = {'user_id': 'test-user', 'text_question': 'Hello there', 'session_id': 'CLI-sessionId', 'projectId': 'CA2020',
#         'overrides': {'BOT_LIST': ['coherence_bot', 'news_bot_v2', 'wiki_bot_mongo'],
#                       'PRIORITY_BOTS': [['news_bot_v2', 'wiki_bot_mongo'], 'coherence_bot']
#                       },
#         'history': ['General Kenobi! You are a bold one.']
#         }
data = {'message': 'Hello there',
        'history': ['General Kenobi! You are a bold one.'],
        'test': True
        }


project_root = Path(__file__).parent.parent.parent.parent
test_data_dir = project_root/'ayesaac'/'data'/'test'

multipart_form_data = (
    ('image', ('custom_file_name.zip', open(str(test_data_dir/'nice_dog.jpg'), 'rb'))),
    ('message', (None, 'who is a good boy'))#,
    # ('path', (None, '/path1')),
    # ('path', (None, '/path2')),
    # ('path', (None, '/path3')),
)


def check_result(response):
    print(response.status_code)
    try:
        print(response.json())

    except Exception as e:
        if type(e) is json.decoder.JSONDecodeError:
            print(str(response))
        else:
            # I guess this wasn't fully formed - oh well
            raise e


if __name__ == '__main__':
    print(f"Sending message: {data['message']}")
    print("Sending...")
    r = requests.get(url="http://localhost:5000/", timeout=(5, 40))
    print(f"Ping response: {r.status_code}")

    try:
        print("Sending test json...")
        r = requests.post(url="http://localhost:5000/submit", json=data, timeout=(5, 40))
    except Exception as e:
        print(f"That didn't work: {e.args}")

    print("Done!")
    check_result(r)
    try:
        print("Sending formData...")
        r = requests.post(url="http://localhost:5000/submit", files=multipart_form_data, timeout=(5, 40))
    except Exception as e:
        print(f"That didn't work: {e.args}")

    print("Done!")
    check_result(r)