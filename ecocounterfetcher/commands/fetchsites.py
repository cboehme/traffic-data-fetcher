import argparse
import csv
from enum import Enum

from ecocounterfetcher import apiclient
from ecocounterfetcher.apiclient import MeansOfTransport


class Columns(Enum):
    ID = "id"
    DOMAIN_ID = "domain_id"
    NAME = "name"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    DIRECTION_IN = "direction_in"
    DIRECTION_OUT = "direction_out"
    MEANS_OF_TRANSPORT_COUNT = "means_of_transport_count"
    MAIN_MEANS_OF_TRANSPORT = "main_means_of_transport"
    START_OF_COLLECTION = "start_of_collection"
    MESSAGE = "message"


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
                       action="extend",
                       nargs="+")
    parser.add_argument("-f", "--file",
                        help="file for storing the fetched data. Data is stored as csv. Existing files are overwritten.",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))


def fetch_sites(domain_id, site_ids, file, **kwargs):
    if domain_id is not None:
        site_ids = _fetch_site_ids_for_domain(domain_id)
    _fetch_and_save_sites(file, site_ids)


def _fetch_site_ids_for_domain(domain_id):
    sites = apiclient.fetch_sites_in_domain(domain_id)
    return [site["idPdc"] for site in sites]


def _fetch_and_save_sites(file, site_ids):
    csv_file = _open_csv(file)
    for site_id in site_ids:
        site = apiclient.fetch_site(site_id)
        site_row = _map_site_to_row(site)
        csv_file.writerow(site_row)


def _open_csv(file):
    column_names = [column.value for column in Columns]
    csv_file = csv.DictWriter(file, column_names, restval="",
                              extrasaction="ignore", dialect="unix")
    csv_file.writeheader()
    return csv_file


def _map_site_to_row(site):
    return {
        Columns.ID.value: site["idPdc"],
        Columns.DOMAIN_ID.value: site["domaine"],
        Columns.NAME.value: site["titre"],
        Columns.LATITUDE.value: site["latitude"],
        Columns.LONGITUDE.value: site["longitude"],
        Columns.DIRECTION_IN.value: site["directionIn"],
        Columns.DIRECTION_OUT.value: site["directionOut"],
        Columns.MEANS_OF_TRANSPORT_COUNT.value: site["nbPratiques"],
        Columns.MAIN_MEANS_OF_TRANSPORT.value: MeansOfTransport(site["pratique"]).name.lower(),
        Columns.START_OF_COLLECTION.value: site["date"],
        Columns.MESSAGE.value: site["message"]
    }
