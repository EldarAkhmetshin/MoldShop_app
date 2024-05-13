from json import loads
from os import environ
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Environment variables not loaded because file .env is missing')
else:
    load_dotenv()
    users = loads(environ.get('USERS'))
