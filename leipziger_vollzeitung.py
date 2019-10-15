#!/usr/bin/env python3

from lib.arguments import arguments
from lib.convert import Convert
from lib.extra import lvz_fetch_full
from lib.generate import Generate

BASE_URL = 'https://www.lvz.de'
FEED_INPUT = {
    name: ''.join([
        BASE_URL, '/rss/feed/', name
    ]) for name in (
        'lvz_kultur',
        'lvz_leipzig',
        'lvz_mitteldeutschland',
        'lvz_nachrichten',
        'lvz_ratgeber',
        'lvz_region',
        'lvz_reise',
        'lvz_sport',
    )
}


def main():
    args = arguments(__file__, FEED_INPUT)
    conv = Convert(args, FEED_INPUT, extra=lvz_fetch_full)
    return 0 if Generate(conv)(BASE_URL) else 1


if __name__ == '__main__':
    exit(main())
