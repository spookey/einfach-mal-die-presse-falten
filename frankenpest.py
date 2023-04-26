#!/usr/bin/env python3

from sys import exit as _exit

from lib.arguments import arguments
from lib.convert import Convert
from lib.extra import frankenpest_fetch_full
from lib.generate import Generate

BASE_URL = "https://www.frankenpost.de"
FEED_INPUT = {
    name: "".join([BASE_URL, "/", name, ".rss.feed"])
    for name in (
        "topmeldung",
        "auf-einen-blick",
        "region",
        "region/hof",
        "region/rehau",
        # 'region/naila',
        # 'region/muenchberg',
        "region/fichtelgebirge",
        "region/wunsiedel",
        "region/marktredwitz",
        "region/selb",
        "region/arzberg",
        # 'region/kulmbach',
        "sport/ver_selb",
        "sport/bayern_hof",
    )
}


def main():
    args = arguments(__file__, FEED_INPUT)
    conv = Convert(args, FEED_INPUT, extra=frankenpest_fetch_full)
    return 0 if Generate(conv)(BASE_URL) else 1


if __name__ == "__main__":
    _exit(main())
