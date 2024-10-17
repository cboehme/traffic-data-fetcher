import argparse
import json

from ecocounterfetcher.apiclient import fetch_site, fetch_sites_in_domain
from ecocounterfetcher.commands import fetchsites, fetchdata


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    fetchsites.register_argparser(subparsers)
    fetchdata.register_argparser(subparsers)

    return parser

def main():
    args = init_argparse().parse_args()
    if hasattr(args, "func"):
        args.func(**vars(args))


if __name__ == "__main__":
    main()
