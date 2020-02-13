import requests
# from utils.address import address
from utils.dict_query import DictQuery

data = {'user_id': 'test-user', 'question': 'Hello there', 'session_id': 'CLI-sessionId', 'projectId': 'CA2020',
        'overrides': {'BOT_LIST': ['coherence_bot', 'news_bot_v2', 'wiki_bot_mongo'],
                      'PRIORITY_BOTS': [['news_bot_v2', 'wiki_bot_mongo'], 'coherence_bot']
                      }
        }

if __name__ == '__main__':
    print(f"Sending text: {data['question']}")
    print("Sending...")
    r = requests.post(url="http://localhost:5130/", json=data)
    print("Done!")
    print(r.status_code)
    print(r.json())
    try:
        print(r.json()[0]['result'])
    except Exception as e:
        # I guess this wasn't fully formed - oh well
        raise e
