import argparse
import json

from ecocounterfetcher.apiclient import fetch_site, fetch_sites_in_domain
from ecocounterfetcher.commands import fetchsites, fetchdata


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    fetchsites.register_argparser(subparsers)
    fetchdata.register_argparser(subparsers)

    list_parser = subparsers.add_parser("list", help="list available counters")
    list_parser.set_defaults(func=list_counters)
    list_parser.add_argument("-d", "--domain",
                             help="id of the domain",
                             required=True,
                             dest="domain_id",
                             type=int)

    info_parser = subparsers.add_parser("info", help="print information about a counter")
    info_parser.set_defaults(func=show_counter)
    info_parser.add_argument("-c", "--counter",
                             help="id of the counter",
                             required=True,
                             dest="counter_id",
                             type=int)

    return parser


def list_counters(domain_id, **kwargs):
    counters = fetch_sites_in_domain(domain_id)
    for counter in counters:
        print("%s: %s" % (counter["idPdc"], counter["nom"]))
    print(json.dumps(counters, indent=4))


def show_counter(counter_id, **kwargs):
    counter = fetch_site(counter_id)
    print(json.dumps(counter, indent=4))




def main():
    args = init_argparse().parse_args()
    if hasattr(args, "func"):
        args.func(**vars(args))


if __name__ == "__main__":
    main()
