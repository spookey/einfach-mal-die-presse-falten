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
TREAT_FIELDS = ('guid', 'link', 'title', 'description')
OUTPUT_FIELDS = ('guid', 'link', 'title', 'pubDate')


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


class Input(object):
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

    @property
    def items(self):
        return self.doc.getElementsByTagName('item')

    @staticmethod
    def entry(item):
        for elem in item.childNodes:
            elem.normalize()
            cont = unescape(
                elem.firstChild.data if elem.hasChildNodes() else elem.data
            ).strip()
            if cont:
                yield elem.nodeName, cont

    @property
    def entries(self):
        for item in self.items:
            result = dict(self.entry(item))
            result.update(origin=self.name)
            yield result


class Treat(object):
    def __init__(self, args):
        self.args = args
        self.now = datetime.utcnow()
        self._cache = None

    def _read(self):
        if exists(self.args.cache):
            with open(self.args.cache, 'r') as op:
                return loads(op.read())
        return []

    def epoch(self, time):
        return int((time - datetime.utcfromtimestamp(0)).total_seconds())

    def stripped(self, cache):
        limit = self.epoch(self.now - timedelta(days=self.args.keep))
        for elem in cache:
            if elem['time'] >= limit:
                yield elem

    @property
    def cache(self):
        if self._cache is None:
            cache = self._read()
            self._cache = list(self.stripped(cache))
        return self._cache

    def _write(self):
        with open(self.args.cache, 'w') as op:
            op.write(dumps(self.cache, indent=2))

    @property
    def pull(self):
        time = self.epoch(self.now)
        for entry in [fl for at in [
            Input(name, url).entries for name, url in FEED_INPUT.items()
        ] for fl in at]:
            entry['time'] = time
            yield entry

    def append(self, entry):
        if entry['title'].strip().startswith(self.args.premium):
            return
        for item in self.cache:
            for field in TREAT_FIELDS:
                if entry[field] == item[field]:
                    return
        self._cache.append(entry)

    @property
    def entries(self):
        for entry in self.pull:
            self.append(entry)
        self._write()
        return self.cache


class Output(object):
    def __init__(self, args):
        self.args = args
        self.dom = getDOMImplementation().createDocument(None, 'rss', None)
        self.source = Treat(args)

    def append(self, parent, tag, text=None):
        node = self.dom.createElement(tag)
        if text is not None:
            node.appendChild(self.dom.createTextNode(text))
        parent.appendChild(node)
        return node

    @property
    def items(self):
        for entry in self.source.entries:
            item = self.dom.createElement('item')
            for field in OUTPUT_FIELDS:
                self.append(item, field, entry[field])
            self.append(item, 'title', ' - '.join(
                entry[fl] for fl in ['origin', 'description']
            ))
            yield item

    @property
    def feed(self):
        doc = self.dom.documentElement
        doc.setAttribute('version', '2.0')
        chan = self.append(doc, 'channel')
        self.append(chan, 'title', self.args.title)
        self.append(chan, 'link', BASE_URL)
        self.append(chan, 'description', self.args.desc)
        self.append(chan, 'lang', 'de-DE')
        self.append(chan, 'pubDate', format_datetime(self.source.now))
        self.append(chan, 'lastBuildDate', format_datetime(self.source.now))
        for item in self.items:
            chan.appendChild(item)
        return doc.toprettyxml()

    def __call__(self):
        with open(self.args.file, 'w') as op:
            return op.write(self.feed) > 0


if __name__ == '__main__':
    exit(not Output(arguments())())
