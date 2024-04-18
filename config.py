import os
import secrets
import string


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'privet _will day its okey'


class Data:
    SECRET_EMAIL = 'dodik337.github@gmail.com'
    SECRET_PASSWORD = 'nrgz ctgo ignr upwv'


ss = []


def generate_psw(length: int):
    letters_and_digits = string.ascii_letters + string.digits
    crypt_rand_string = ''.join(secrets.choice(
        letters_and_digits) for i in range(length))
    psw_two = ''.join(secrets.choice(
        letters_and_digits) for y in range(length * 2))
    for u in crypt_rand_string:
        if u not in ss:
            ss.append(u)
    for t in psw_two:
        if t not in ss:
            ss.append(t)
    return ''.join(ss)
