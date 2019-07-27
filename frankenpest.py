#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime, timedelta
from email.utils import format_datetime
from html import unescape
from json import dumps, loads
from os.path import exists
from urllib.request import urlopen
from xml.dom.minidom import getDOMImplementation, parseString

BASE_URL = 'http://www.frankenpost.de/'
FEED_INPUT = dict((
    name, ''.join([
        BASE_URL, 'storage/rss/rss/fp/', name, '.xml'
    ])
) for name in (
    'topmeldung',
    'homepage',
    'nachrichten_hofrehau',
    'nachrichten_fichtelgebirge',
    'nachrichten_selb',
    'nachrichten_kulmbach',
    'nachrichten_muenchberg',
    'nachrichten_naila',
    'nachrichten_regional',
    'nachrichten_kultur',
    'nachrichten_wirtschaft',
    'sport_verselb',
))


def arguments():
    def _help(txt):
        return '{} (default: "%(default)s")'.format(txt)

    parser = ArgumentParser(__file__, epilog='-.-')
    parser.add_argument(
        '-f', '--file', default='frankenpest.xml',
        help=_help('output feed filename'),
    )
    parser.add_argument(
        '-c', '--cache', default='frankenpest.json',
        help=_help('content cache filename'),
    )
    parser.add_argument(
        '-k', '--keep', default=14, type=int,
        help=_help('days to keep cache entries'),
    )
    parser.add_argument(
        '-p', '--premium', default='***',
        help=_help('title prefix for premium articles'),
    )
    parser.add_argument(
        '-t', '--title', default='Frankenpest',
        help=_help('feed title'),
    )
    parser.add_argument(
        '-d', '--desc', default='Frankenpest Breaking News',
        help=_help('feed description'),
    )
    return parser.parse_args()


class Input:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self._doc = None

    @property
    def doc(self):
        if self._doc is None:
            with urlopen(self.url) as resp:
                doc = resp.read().decode('ISO-8859-1')
                self._doc = parseString(doc)
        return self._doc

    @staticmethod
    def entry(item):
        for elem in item.childNodes:
            elem.normalize()
            cont = unescape(
                elem.firstChild.data if elem.hasChildNodes() else elem.data
            ).strip()
            if cont:
                yield elem.nodeName, cont

    def __call__(self):
        for item in self.doc.getElementsByTagName('item'):
            result = dict(self.entry(item))
            result.update(origin=self.name)
            yield result


class Treat:
    def __init__(self, args):
        self.args = args
        self.now = datetime.utcnow()

    def _read(self):
        if exists(self.args.cache):
            with open(self.args.cache, 'r') as handle:
                return loads(handle.read())
        return []

    @staticmethod
    def epoch(time):
        return int((time - datetime.utcfromtimestamp(0)).total_seconds())

    def limited_order(self, cache):
        limit = self.epoch(self.now - timedelta(days=self.args.keep))
        return list(sorted(
            (elem for elem in cache if elem['time'] >= limit),
            key=lambda el: el['time'], reverse=True
        ))

    def _write(self, cache):
        with open(self.args.cache, 'w') as handle:
            handle.write(dumps(cache, indent=2))

    @property
    def pull(self):
        time = self.epoch(self.now)
        for entry in [fl for at in [
                Input(name, url)() for name, url in FEED_INPUT.items()
        ] for fl in at]:
            entry['time'] = time
            yield entry

    def valuable(self, cache, entry):
        if entry['title'].strip().startswith(self.args.premium):
            return False
        fields = ('guid', 'link', 'title', 'description')
        for item in cache:
            for field in fields:
                if entry[field] == item[field]:
                    return False
        return True

    def __call__(self):
        cache = self._read()
        for entry in self.pull:
            if self.valuable(cache, entry):
                cache.append(entry)
        cache = self.limited_order(cache)
        self._write(cache)
        return cache


class Output:
    def __init__(self, args):
        self.args = args
        self.treat = Treat(args)
        self.dom = getDOMImplementation().createDocument(None, 'rss', None)

    def append(self, parent, tag, text=None, data=False):
        node = self.dom.createElement(tag)
        if text is not None:
            node.appendChild((
                self.dom.createCDATASection
                if data else
                self.dom.createTextNode
            )(text))
        parent.appendChild(node)
        return node

    @property
    def items(self):
        fields = ('guid', 'link', 'pubDate')
        for entry in self.treat():
            item = self.dom.createElement('item')
            self.append(item, 'title', entry['title'], True)
            for field in fields:
                self.append(item, field, entry[field])
            self.append(item, 'description', '{} - {}'.format(
                entry['origin'].split('_')[-1].upper(),
                entry['description']
            ), True)
            yield item

    @property
    def feed(self):
        doc = self.dom.documentElement
        doc.setAttribute('version', '2.0')
        chan = self.append(doc, 'channel')
        self.append(chan, 'title', self.args.title)
        self.append(chan, 'link', BASE_URL)
        self.append(chan, 'description', self.args.desc)
        self.append(chan, 'language', 'de-DE')
        self.append(chan, 'pubDate', format_datetime(self.treat.now))
        self.append(chan, 'lastBuildDate', format_datetime(self.treat.now))
        for item in self.items:
            chan.appendChild(item)
        return doc.toprettyxml(
            indent='  ', encoding='utf-8'
        ).decode('utf-8')

    def __call__(self):
        feed = self.feed
        with open(self.args.file, 'w') as handle:
            return handle.write(feed) > 0


if __name__ == '__main__':
    exit(not Output(arguments())())
