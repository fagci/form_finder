#!/usr/bin/env python3
from sys import argv
from urllib.parse import urlparse, urlunsplit, urljoin

from bs4 import BeautifulSoup
from requests import Session


class FF(Session):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.loot = {}
        self.urls = set()

    def crawl(self, url):
        print('[*]', url)
        self.urls.add(url)
        html = self.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
        s = BeautifulSoup(html, 'html.parser')
        for form in s('form'):
            action = form.get('action', '')
            form_action = self.normalize_uri(action)
            form_fields = [
                f.get('name') for f in form.select('[name]')
                if f.has_attr('required')
            ]
            print('[+]', form.get('id'), form_action, form_fields)
            self.loot[form_action] = form_fields

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
