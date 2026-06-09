

import requests

token =''

from settings import token

print(token)

import os

for env in os.environ.items():
    print(env)

TOKEN = os.getenv('c')
