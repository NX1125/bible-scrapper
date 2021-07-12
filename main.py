import dataclasses
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup

URL = 'biblegateway.com'


@dataclasses.dataclass
class Book:
    display: str
    chapters: list[int]


verse_pattern = re.compile(r'\d+\s*(.*)')
whitespace_pattern = re.compile(r'\s+')

if __name__ == '__main__':
    with open('books.json', 'r', encoding='utf-8') as file:
        data = json.load(file)['data'][0]

    books = [Book(node['display'], [chapter['chapter'] for chapter in node['chapters']]) for node in data]
    print(f'There are {len(books)} books to extract')

    try:
        os.mkdir('out')
    except FileExistsError:
        pass

    count = sum(len(book.chapters) for book in books)
    i = 0

    for book in books:
        print(f'Extracting {len(book.chapters)} chapters from {book.display}')
        for chapter in book.chapters:
            print(f'Fetching {book.display} {chapter}')
            response = requests.get('https://www.biblegateway.com/passage/', {
                'search': f'{book.display} {chapter}',
                'version': 'RVA',
            })

            assert response.status_code == 200, response.status_code

            print('Parsing verses')
            soup = BeautifulSoup(response.text, features='html.parser')
            verses = [
                whitespace_pattern.sub(' ', verse_pattern.match(verse.text).group(1).strip())
                for verse in soup.select('div.passage-text div.version-RVA p.verse')
            ]

            print(f'Writing {len(verses)} verses')
            with open(f'out/{book.display}_{chapter}.txt', 'w', encoding='utf-8') as file:
                file.writelines(map('{}\n\n'.format, verses))

            i += 1
            print(f'{i / count:.02%}% completed')

            time.sleep(0.6)

