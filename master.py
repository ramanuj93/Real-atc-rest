import json

global credentials


def transform(recieved):
    print(received)




received = input()
with open('./credentials.cred') as f:
    credentials = json.load(f)


transform(received)