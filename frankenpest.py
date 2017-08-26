#!/usr/bin/env python3

from sys import argv
from email.utils import format_datetime
from datetime import datetime
from urllib.request import urlopen
from xml.dom.minidom import parseString, getDOMImplementation

FEED_ENCODING = 'ISO-8859-1'
FEED_INPUT = dict((
    name, ''.join([
        'http://www.frankenpost.de/storage/rss/rss/fp/', name, '.xml'
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


class Input(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self._doc = None

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)

    @property
    def doc(self):
        if self._doc is None:
            with urlopen(self.url) as resp:
                doc = resp.read().decode(FEED_ENCODING)
                self._doc = parseString(doc)
        return self._doc

    @property
    def items(self):
        return self.doc.getElementsByTagName('item')

    @staticmethod
    def entry(item):
        for elem in item.childNodes:
            elem.normalize()
            cont = (
                elem.firstChild.data if elem.hasChildNodes() else elem.data
            ).strip()
            if cont:
                yield elem.nodeName, cont

    @property
    def entries(self):
        result = []
        for item in self.items:
            res = dict(self.entry(item))
            res.update(item=item)
            result.append(res)
        return result


class Output(object):
    def __init__(self):
        self.dom = getDOMImplementation().createDocument(None, 'rss', None)

    @property
    def entries(self):
        guids = []
        for entry in [fl for at in [
                Input(name, url).entries for name, url in FEED_INPUT.items()
        ] for fl in at]:
            if entry['title'].startswith('***'):
                continue

            if entry['guid'] not in guids:
                yield entry['item']
            guids.append(entry['guid'])

    def append(self, parent, tag, text=None):
        node = self.dom.createElement(tag)
        if text is not None:
            node.appendChild(self.dom.createTextNode(text))
        parent.appendChild(node)
        return node

    @property
    def feed(self):
        doc = self.dom.documentElement
        doc.setAttribute(
            'xmlns:dc', 'http://purl.org/dc/elements/1.1/'
        )
        doc.setAttribute(
            'xmlns:admin', 'http://webns.net/mvcb/'
        )
        doc.setAttribute(
            'xmlns:rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        )
        doc.setAttribute(
            'xmlns:content', 'http://purl.org/rss/1.0/modules/content/'
        )
        doc.setAttribute(
            'version', '2.0'
        )
        chan = self.append(doc, 'channel')
        fnow = format_datetime(datetime.now())
        self.append(chan, 'title', 'Frankenpest')
        self.append(chan, 'link', 'http://www.frankenpost.de/')
        self.append(chan, 'description', 'Frankenpest Breaking News')
        self.append(chan, 'lang', 'de-DE')
        self.append(chan, 'pubDate', fnow)
        self.append(chan, 'lastBuildDate', fnow)
        for entry in self.entries:
            chan.appendChild(entry)
        return doc.toprettyxml(encoding=FEED_ENCODING)

    def save(self, filename):
        with open(filename, 'wb') as handle:
            handle.write(self.feed)
        return True


if __name__ == '__main__':
    filename = argv[1] if len(argv) > 1 else 'frankenpest.xml'
    exit(not Output().save(filename))
