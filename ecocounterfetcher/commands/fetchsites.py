import argparse
import csv
from enum import auto

from ecocounterfetcher import apiclient
from ecocounterfetcher.apiclient import MeansOfTransport
from ecocounterfetcher.utilfunctions import fetch_site_ids_for_domain, open_csv
from ecocounterfetcher.types import EnumWithLowerCaseNames


class Columns(EnumWithLowerCaseNames):
    ID = auto()
    DOMAIN_ID = auto()
    NAME = auto()
    LATITUDE = auto()
    LONGITUDE = auto()
    DIRECTION_IN = auto()
    DIRECTION_OUT = auto()
    MEANS_OF_TRANSPORT_COUNT = auto()
    MAIN_MEANS_OF_TRANSPORT = auto()
    START_OF_COLLECTION = auto()
    MESSAGE = auto()


def register_argparser(subparsers):
    parser = subparsers.add_parser("fetch-sites", help="fetch site descriptions")
    parser.set_defaults(func=fetch_sites)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain",
                       help="id of the domain whose counter sites should be fetched",
                       dest="domain_id",
                       type=int)
    group.add_argument("-s", "--sites",
                       help="ids of the counter sites to fetch",
                       dest="site_ids",
                       type=int,
                       nargs="+")
    parser.add_argument("-f", "--file",
                        help="file for storing the fetched data. Data is stored as csv. Existing files are overwritten.",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))


def fetch_sites(domain_id, site_ids, file, **kwargs):
    if domain_id is not None:
        site_ids = fetch_site_ids_for_domain(domain_id)
    _fetch_and_save_sites(file, site_ids)


def _fetch_and_save_sites(file, site_ids):
    csv_file = open_csv(file, Columns)
    for site_id in site_ids:
        site = apiclient.fetch_site(site_id)
        site_row = _map_site_to_row(site)
        csv_file.writerow(site_row)


def _map_site_to_row(site):
    return {
        Columns.ID: site["idPdc"],
        Columns.DOMAIN_ID: site["domaine"],
        Columns.NAME: site["titre"],
        Columns.LATITUDE: site["latitude"],
        Columns.LONGITUDE: site["longitude"],
        Columns.DIRECTION_IN: site["directionIn"],
        Columns.DIRECTION_OUT: site["directionOut"],
        Columns.MEANS_OF_TRANSPORT_COUNT: site["nbPratiques"],
        Columns.MAIN_MEANS_OF_TRANSPORT: MeansOfTransport(site["pratique"]),
        Columns.START_OF_COLLECTION: site["date"],
        Columns.MESSAGE: site["message"]
    }
