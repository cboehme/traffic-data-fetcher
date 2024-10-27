import argparse

from ecocounterfetcher.commands import fetchsites, fetchdata, finddomains, \
    fetchdomains
from ecocounterfetcher.commands.fetchdomains import fetch_domains


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    fetchdomains.register_argparser(subparsers)
    fetchsites.register_argparser(subparsers)
    fetchdata.register_argparser(subparsers)
    finddomains.register_argparser(subparsers)

    return parser

def main():
    args = init_argparse().parse_args()
    if hasattr(args, "func"):
        args.func(**vars(args))


if __name__ == "__main__":
    main()
