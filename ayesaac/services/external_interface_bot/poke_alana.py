import requests
# from utils.address import address


# data = {'user_id': 'test-user', 'text_question': 'Hello there', 'session_id': 'CLI-sessionId', 'projectId': 'CA2020',
#         'overrides': {'BOT_LIST': ['coherence_bot', 'news_bot_v2', 'wiki_bot_mongo'],
#                       'PRIORITY_BOTS': [['news_bot_v2', 'wiki_bot_mongo'], 'coherence_bot']
#                       },
#         'history': ['General Kenobi! You are a bold one.']
#         }
data = {'text_question': 'Hello there',
        'history': ['General Kenobi! You are a bold one.']
        }

if __name__ == '__main__':
    print(f"Sending text: {data['text_question']}")
    print("Sending...")
    r = requests.post(url="http://localhost:5130", json=data)

    print("Done!")
    print(r.status_code)
    try:
        print(r.json())  # r.json()[0]['uid']
    except Exception as e:
        # I guess this wasn't fully formed - oh well
        raise e
