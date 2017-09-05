#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from email.utils import format_datetime
from urllib.request import urlopen
from xml.dom.minidom import getDOMImplementation, parseString

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


def arguments():
    parser = ArgumentParser(__file__, epilog='-.-')
    parser.add_argument(
        '-f', '--file', default='frankenpest.xml',
        help='output feed filename (default: %(default)s)',
    )
    parser.add_argument(
        '-p', '--premium', default='***',
        help='title prefix for premium articles (default: %(default)s)',
    )
    parser.add_argument(
        '-t', '--title', default='Frankenpest',
        help='feed title (default: %(default)s)',
    )
    parser.add_argument(
        '-d', '--desc', default='Frankenpest Breaking News',
        help='feed description (default: %(default)s)',
    )
    return parser.parse_args()


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
    def __init__(self, args):
        self.args = args
        self.dom = getDOMImplementation().createDocument(None, 'rss', None)

    @property
    def entries(self):
        fields = ('guid', 'title', 'description')
        tracked = set()
        for entry in [fl for at in [
            Input(name, url).entries for name, url in FEED_INPUT.items()
        ] for fl in at]:
            if entry['title'].lstrip().startswith(self.args.premium):
                continue

            if all(entry[fld].strip() not in tracked for fld in fields):
                [tracked.add(entry[fld].strip()) for fld in fields]
                yield entry['item']

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
        self.append(chan, 'title', self.args.title)
        self.append(chan, 'link', 'http://www.frankenpost.de/')
        self.append(chan, 'description', self.args.desc)
        self.append(chan, 'lang', 'de-DE')
        self.append(chan, 'pubDate', fnow)
        self.append(chan, 'lastBuildDate', fnow)
        for entry in self.entries:
            chan.appendChild(entry)
        return doc.toprettyxml()

    def save(self):
        with open(self.args.file, 'w') as handle:
            handle.write(self.feed)
        return True


if __name__ == '__main__':
    exit(not Output(arguments()).save())
