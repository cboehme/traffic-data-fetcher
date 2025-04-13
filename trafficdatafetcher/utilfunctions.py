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
import csv

from trafficdatafetcher import apiclient


def positive_value(value):
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return int_value


def fetch_site_ids_for_domain(domain_id):
    sites = apiclient.fetch_sites_in_domain(domain_id)
    return [site["lienPublic"] for site in sites if site["lienPublic"] is not None]


def open_csv(file, columns):
    csv_file = csv.DictWriter(file, columns, restval="",
                              extrasaction="ignore", dialect="unix")
    csv_file.writeheader()
    return csv_file
