import os
import sys
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore


def check_url(url):
    return '.' in url


def save_url_content(url, content):
    with open(url, 'w') as f:
        print(*content, sep='\n', file=f)


def get_url_content(url):
    content = None
    with open(url) as f:
        content = f.read()
    return content


def text_no_tags(tree, tags):
    text = []
    tag = tree.find(tags)
    while tag:
        extract = tag.extract()
        if extract.name == 'a' and extract.string:
            extract.string.insert_before(Fore.BLUE)
        for a in extract.find_all('a'):
            if a.string:
                a.string.insert_before(Fore.BLUE)
        text.append(' '.join([*extract.stripped_strings]))
        tag = tree.find(tags)
    return text


init(autoreset=True)
dir_path = sys.argv[1] if len(sys.argv) > 1 else "tb_tabs"
if not os.path.exists(dir_path):
    os.mkdir(dir_path)
os.chdir(dir_path)
prev_stack = []
while True:
    user_input = input()
    if user_input == "exit":
        break
    if user_input == "back" and prev_stack:
        prev_stack.pop()
        print(get_url_content(prev_stack.pop()))
    elif os.path.isfile(user_input):
        prev_stack.append(user_input)
        print(get_url_content(user_input))
    elif check_url(user_input):
        no_domain = '.'.join(user_input.split('.')[:-1])
        if not user_input.startswith("http"):
            user_input = "https://" + user_input
        r = requests.get(user_input)
        soup = BeautifulSoup(r.content, 'html.parser')
        tags_text = ('p',
                     'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                     'a',
                     'ul', 'ol', 'li')
        text_content = text_no_tags(soup.body, tags_text)
        save_url_content(no_domain, text_content)
        prev_stack.append(no_domain)
        print(*text_content, sep='\n')
    else:
        print("Error: No such tab or Incorrect URL")
        
os.chdir('..')
