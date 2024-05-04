from argparse import ArgumentParser
from os import path


def arguments(name, excludes):
    name, *_ = path.splitext(path.basename(name))
    title = " ".join(nm.capitalize() for nm in name.split("_"))
    file = f"{name}{path.extsep}xml"
    cache = f"{name}{path.extsep}json"

    def _help(text):
        return f'{text} (default "%(default)s")'

    parser = ArgumentParser(name, epilog="-.-")
    parser.add_argument(
        "-f",
        "--file",
        default=file,
        help=_help("output feed filename"),
    )
    parser.add_argument(
        "-c",
        "--cache",
        default=cache,
        help=_help("content cache filename"),
    )
    parser.add_argument(
        "-k",
        "--keep",
        default=14,
        type=int,
        help=_help("days to keep cache entries"),
    )
    parser.add_argument(
        "-t",
        "--title",
        default=title,
        help=_help("feed title"),
    )
    parser.add_argument(
        "-d",
        "--desc",
        default=f"{title} Breaking News",
        help=_help("feed description"),
    )
    parser.add_argument(
        "-l",
        "--language",
        default="de-DE",
        help=_help("feed language"),
    )
    parser.add_argument(
        "-x",
        "--excludes",
        nargs="*",
        default=[],
        choices=excludes,
        help="exclude some feeds from output",
    )

    return parser.parse_args()
