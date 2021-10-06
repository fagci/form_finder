#!/usr/bin/env python3
from sys import argv
from urllib.parse import urljoin, urlparse, urlunsplit

from bs4 import BeautifulSoup
from requests import Session


class FF(Session):
    HEADERS = {'User-Agent': 'Mozilla/5.0'}

    def __init__(self, base):
        super().__init__()
        self.base = base
        self.loot = {}
        self.urls = set()

    def crawl(self, url):
        self.urls.add(url)
        html = self.get(url, headers=FF.HEADERS).text
        s = BeautifulSoup(html, 'html.parser')

        for form in s('form'):
            action = form.get('action') or url
            form_action = self.normalize_uri(action)
            if form_action in self.loot:
                continue

            fields_required = []
            fields_optional = []

            for f in form.select('[name]'):
                name = f.get('name')
                if f.has_attr('required'):
                    fields_required.append(name)
                else:
                    fields_optional.append(name)

            print('[+]', url)
            print('Action:', form_action)
            if fields_required:
                print('Required:', ', '.join(fields_required))
            if fields_optional:
                print('Optional:', ', '.join(fields_optional))
            print()
            self.loot[form_action] = (fields_required, fields_optional)

        for a in s('a'):
            href = a.get('href')
            if not href:
                continue

            next_url = self.normalize_uri(href)
            if next_url in self.urls:
                continue

            if next_url.startswith(self.base):
                self.crawl(next_url)

    def run(self):
        self.crawl(self.base)

    def normalize_uri(self, uri):
        new = urlparse(urljoin(self.base, uri).lower())
        return urlunsplit((new.scheme, new.netloc, new.path, new.query, ''))


def main(base):
    ff = FF(base)
    ff.run()


if __name__ == '__main__':
    main(argv[1])
