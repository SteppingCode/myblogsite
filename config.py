import os

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'privet _will day its okey'