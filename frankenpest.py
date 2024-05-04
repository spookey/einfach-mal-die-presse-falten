#!/usr/bin/env python3

from sys import exit as _exit

from lib.arguments import arguments
from lib.convert import Convert
from lib.extra import frankenpest_fetch_full
from lib.generate import Generate

BASE_URL = "https://www.frankenpost.de"
FEED_INPUT = {
    name: f"{BASE_URL}/{name}.rss2.feed"
    for name in (
        "topmeldung",
        "auf-einen-blick",
        "region",
        "region/hof",
        "region/rehau",
        "region/naila",
        "region/muenchberg",
        "region/fichtelgebirge",
        "region/wunsiedel",
        "region/marktredwitz",
        "region/selb",
        "region/arzberg",
        "region/kulmbach",
        "sport/ver_selb",
        "sport/bayern_hof",
    )
}


def main():
    args = arguments(__file__, FEED_INPUT)
    convert = Convert(args, FEED_INPUT, extra=frankenpest_fetch_full)
    generate = Generate(convert)

    if not generate(BASE_URL):
        return 1
    return 0


if __name__ == "__main__":
    _exit(main())
