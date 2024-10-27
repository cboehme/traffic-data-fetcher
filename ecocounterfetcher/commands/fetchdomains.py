import argparse
from enum import auto

from ecocounterfetcher import apiclient
from ecocounterfetcher.types import EnumWithLowerCaseNames
from ecocounterfetcher.utilfunctions import open_csv


class Columns(EnumWithLowerCaseNames):
    DOMAIN_ID = auto()
    NAME = auto()


def register_argparser(subparsers):
    parser = subparsers.add_parser("fetch-domains", help="Fetch a list of all known domains")
    parser.set_defaults(func=fetch_domains)
    parser.add_argument("-f", "--file",
                        help="file for storing the fetched data. Data is stored as csv. Existing files are overwritten.",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))


def fetch_domains(file, **kwargs):
    csv_file = open_csv(file, Columns)
    domains = apiclient.fetch_domains()
    for domain in domains:
        csv_file.writerow(_map_site_list_to_row(domain))


def _map_site_list_to_row(domain):
    return {
        Columns.DOMAIN_ID: domain['id'],
        Columns.NAME: domain['name']
    }
