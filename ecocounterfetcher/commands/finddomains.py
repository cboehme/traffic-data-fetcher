import argparse
from enum import auto

from ecocounterfetcher import apiclient
from ecocounterfetcher.types import EnumWithLowerCaseNames
from ecocounterfetcher.utilfunctions import open_csv, positive_value


class Columns(EnumWithLowerCaseNames):
    DOMAIN_ID = auto()
    NAME = auto()


def register_argparser(subparsers):
    parser = subparsers.add_parser("find-domains", help="query all domain ids between 1 and 10000 to generate a list of known domains")
    parser.set_defaults(func=find_domains)
    parser.add_argument("-f", "--file",
                        help="file for storing the fetched data. Data is stored as csv. Existing files are overwritten.",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))
    parser.add_argument("-m", "--max-domain-id",
                        help="max domain id to search for",
                        default=10000,
                        dest="max_domain_id",
                        type=positive_value)


def find_domains(file, max_domain_id, **kwargs):
    csv_file = open_csv(file, Columns)
    for domain_id in range(1, max_domain_id):
        print("Trying domain id %d" % domain_id)
        sites = apiclient.fetch_sites_in_domain(domain_id)
        if len(sites) > 0:
            csv_file.writerow(_map_site_list_to_row(domain_id, sites))


def _map_site_list_to_row(domain_id, sites):
    return {
        Columns.DOMAIN_ID: domain_id,
        Columns.NAME: sites[0]['nomOrganisme']
    }
