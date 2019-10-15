#!/usr/bin/env python3

from lib.arguments import arguments
from lib.convert import Convert
from lib.extra import fp_arg_premium
from lib.generate import Generate

BASE_URL = 'http://www.frankenpost.de'
FEED_INPUT = {
    name: ''.join([
        BASE_URL, '/storage/rss/rss/fp/', name, '.xml'
    ]) for name in (
        'homepage',
        'nachrichten_fichtelgebirge',
        'nachrichten_hofrehau',
        'nachrichten_kulmbach',
        'nachrichten_kultur',
        'nachrichten_muenchberg',
        'nachrichten_naila',
        'nachrichten_regional',
        'nachrichten_selb',
        'nachrichten_wirtschaft',
        'sport_verselb',
        'topmeldung',
    )
}


def main():
    args = arguments(__file__, FEED_INPUT, extra=fp_arg_premium)
    conv = Convert(args, FEED_INPUT, encoding='ISO-8859-1')
    return 0 if Generate(conv)(BASE_URL) else 1


if __name__ == '__main__':
    exit(main())
