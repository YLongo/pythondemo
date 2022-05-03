import os.path
import sys

import requests

# sys.path.append(path.abspath('../deepl-translate'))
# deepl = __import__("deepl")

from deepl.api import translate

proxies = {
    'http': 'http://127.0.0.1:1080',
    'https': 'http://127.0.0.1:1080'
}


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(sys.path)  # Press Ctrl+F8 to toggle the breakpoint.
    # print(deepl)


# Press the green button in the gutter to run the script.

def translate_deepL(text):
    source_language = "EN"
    target_language = "ZH"
    # text = "We can add the path to the root of the project:"
    # expected_translation = "hello"
    translation = translate(source_language, target_language, text)
    print("translation:", translation)


def new_top_stories():
    top_story_url = "https://hacker-news.firebaseio.com/v0/topstories.json"

    count = 0
    with requests.get(top_story_url, proxies=proxies) as response:
        response_json = response.json()
        print(response_json)
        for id in response_json:
            item_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
            if count < 10:
                print(id)
                item_url = item_url.format(id)
                print(item_url)
                count += 1
                get_item(item_url)
            else:
                break


def get_item(url):
    with requests.get(url, proxies=proxies) as response:
        item = response.json()
        type_ = item['type']
        if type_ == 'story':
            title_ = item['title']
            print(title_)
            translate_deepL(title_)


if __name__ == '__main__':
    # print_hi('PyCharm')
    # text = "Why Are Some Egg Yolks So Orange?"
    # translate_deepL(text)
    new_top_stories()
