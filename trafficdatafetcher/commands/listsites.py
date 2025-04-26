# Traffic Data Fetcher - Retrieve data from Eco Counter's traffic counter API
# Copyright (C) 2025  Christoph Böhne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
from enum import auto

from trafficdatafetcher import apiclient
from trafficdatafetcher.apiclient import MeansOfTransport
from trafficdatafetcher.csvutils import open_csv
from trafficdatafetcher.types import EnumWithLowerCaseNames


class Columns(EnumWithLowerCaseNames):
    ID = auto()
    DOMAIN_ID = auto()
    NAME = auto()
    LATITUDE = auto()
    LONGITUDE = auto()
    PUBLIC = auto()
    DIRECTION_IN = auto()
    DIRECTION_OUT = auto()
    MEANS_OF_TRANSPORT_COUNT = auto()
    MAIN_MEANS_OF_TRANSPORT = auto()
    START_OF_COLLECTION = auto()
    MESSAGE = auto()


def register_argparser(subparsers):
    parser = subparsers.add_parser("list-sites", help="list counter site descriptions")
    parser.set_defaults(func=list_sites)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain",
                       help="id of the domain whose counter sites should be listed",
                       dest="domain_id",
                       type=int)
    group.add_argument("-s", "--sites",
                       help="ids of the counter sites to list",
                       dest="site_ids",
                       type=int,
                       nargs="+")
    parser.add_argument("-f", "--file",
                        help="store counter sites in a csv-file. Existing files are overwritten",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))


def list_sites(domain_id, site_ids, file, **kwargs):
    if domain_id is not None:
        _fetch_and_save_all_sites_in_domain(domain_id, file)
    else:
        _fetch_and_save_sites(file, site_ids)


def _fetch_and_save_all_sites_in_domain(domain_id, file):
    csv_file = open_csv(file, Columns)
    sites = apiclient.fetch_sites_in_domain(domain_id)
    for site in sites:
        if site["lienPublic"] is None:
            site_row = _map_site_to_row(domain_id, site)
        else:
            public_site_id = site["lienPublic"]
            public_site = apiclient.fetch_site(public_site_id)
            site_row = _map_public_site_to_row(public_site)
        csv_file.writerow(site_row)


def _fetch_and_save_sites(file, site_ids):
    csv_file = open_csv(file, Columns)
    for site_id in site_ids:
        site = apiclient.fetch_site(site_id)
        site_row = _map_public_site_to_row(site)
        csv_file.writerow(site_row)


def _map_site_to_row(domain_id, site):
    return {
        Columns.ID: site["idPdc"],
        Columns.DOMAIN_ID: domain_id,
        Columns.NAME: site["nom"],
        Columns.LATITUDE: site["lat"],
        Columns.LONGITUDE: site["lon"],
        Columns.PUBLIC: False,
        Columns.DIRECTION_IN: "",
        Columns.DIRECTION_OUT: "",
        Columns.MEANS_OF_TRANSPORT_COUNT: _calculate_means_of_transport_count(
            site["pratique"]),
        Columns.MAIN_MEANS_OF_TRANSPORT:
            MeansOfTransport(site["mainPratique"]),
        Columns.START_OF_COLLECTION: "",
        Columns.MESSAGE: site["publicMessage"]
     }


def _calculate_means_of_transport_count(counters):
    means_of_transports = {}
    for counter in counters:
        means_of_transports[counter["pratique"]] = True
    return len(means_of_transports)


def _map_public_site_to_row(site):
    return {
        Columns.ID: site["idPdc"],
        Columns.DOMAIN_ID: site["domaine"],
        Columns.NAME: site["titre"],
        Columns.LATITUDE: site["latitude"],
        Columns.LONGITUDE: site["longitude"],
        Columns.PUBLIC: True,
        Columns.DIRECTION_IN: site["directionIn"],
        Columns.DIRECTION_OUT: site["directionOut"],
        Columns.MEANS_OF_TRANSPORT_COUNT: site["nbPratiques"],
        Columns.MAIN_MEANS_OF_TRANSPORT: MeansOfTransport(site["pratique"]),
        Columns.START_OF_COLLECTION: site["date"],
        Columns.MESSAGE: site["message"]
    }
