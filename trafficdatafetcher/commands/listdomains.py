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
from trafficdatafetcher.types import EnumWithLowerCaseNames
from trafficdatafetcher.csvutils import open_csv


class Columns(EnumWithLowerCaseNames):
    DOMAIN_ID = auto()
    NAME = auto()


def register_argparser(subparsers):
    parser = subparsers.add_parser("list-domains", help="list all domains")
    parser.set_defaults(func=list_domains)
    parser.add_argument("-f", "--file",
                        help="store domain list in a csv-file. Existing files are overwritten",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))


def list_domains(file, **kwargs):
    csv_file = open_csv(file, Columns)
    domains = apiclient.fetch_domains()
    for domain in domains:
        csv_file.writerow(_map_site_list_to_row(domain))


def _map_site_list_to_row(domain):
    return {
        Columns.DOMAIN_ID: domain['id'],
        Columns.NAME: domain['name']
    }
