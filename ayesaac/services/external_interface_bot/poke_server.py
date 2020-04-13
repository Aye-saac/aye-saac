import json

import requests
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

if __name__ == '__main__':
    print(f"Sending message: {data['message']}")
    print("Sending...")
    r = requests.get(url="http://localhost:5000/")
    print(f"Ping response: {r.status_code}")
    r = requests.post(url="http://localhost:5000/submit", json=data)

    print("Done!")
    print(r.status_code)
    try:
        print(r.json())

    except Exception as e:
        if type(e) is json.decoder.JSONDecodeError:
            print(str(r))
        else:
            # I guess this wasn't fully formed - oh well
            raise e
