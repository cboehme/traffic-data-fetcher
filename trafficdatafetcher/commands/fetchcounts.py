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
from datetime import date
from enum import auto

from trafficdatafetcher import apiclient
from trafficdatafetcher.apiclient import StepSize, Direction, MeansOfTransport
from trafficdatafetcher.csvutils import open_csv
from trafficdatafetcher.types import EnumWithLowerCaseNames


class Columns(EnumWithLowerCaseNames):
    COUNTER_ID = auto()
    MEANS_OF_TRANSPORT = auto()
    DIRECTION = auto()
    TIMESTAMP = auto()
    COUNT = auto()


def register_argparser(subparsers):
    parser = subparsers.add_parser("fetch-counts", help='fetch counts')
    parser.set_defaults(func=fetch_data)
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
                        help="store data in a csv-file. Existing files are overwritten",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))
    parser.add_argument("-S", "--step-size",
                        help="step size of the data to fetch. Defaults to `hour`",
                        choices=list(StepSize),
                        default=StepSize.HOUR,
                        dest="step_size",
                        type=StepSize.from_string)
    parser.add_argument("-B", "--begin",
                        help="fetch data starting at date. Date must be ISO 8610 formatted (YYYY-MM-DD)",
                        dest="begin",
                        type=date.fromisoformat)
    parser.add_argument("-E", "--end",
                        help="fetch data until date (exclusively). Date must be ISO 8610 formatted (YYYY-MM-DD)",
                         dest="end",
                        type=date.fromisoformat)
    parser.add_argument("-D", "--direction",
                        help="select directions to fetch. By default, data for all directions is fetched",
                        choices=list(Direction),
                        default=list(Direction),
                        dest="direction",
                        type=Direction.from_string,
                        nargs="+")
    parser.add_argument("-M", "--means-of-transport",
                        help="select means of transport to fetch. By default, data for all means of transport is fetched",
                        choices=list(MeansOfTransport),
                        default=list(MeansOfTransport),
                        dest="means_of_transport",
                        type=MeansOfTransport.from_string,
                        nargs="+")


def fetch_data(domain_id, site_ids, step_size, file, begin, end, direction, means_of_transport, **kwargs):
    if domain_id is not None:
        sites = apiclient.fetch_sites_in_domain(domain_id)
        site_ids = [site["lienPublic"] for site in sites if site["lienPublic"] is not None]

    csv_file = open_csv(file, Columns)
    for site_id in site_ids:
        data = _fetch_all_channels(step_size, site_id, begin, end, direction, means_of_transport)
        _save_data(site_id, data, csv_file)


def _fetch_all_channels(step_size, site_id, begin, end, direction, means_of_transport):

    site = apiclient.fetch_site(site_id)

    domain_id = site["domaine"]
    token = site["token"]
    data = {}
    for channel in site["channels"]:
        _fetch_and_merge_channel(data, channel, domain_id, begin, end,
                                 step_size, direction, means_of_transport,
                                 token)
    return data


def _fetch_and_merge_channel(data, channel, domain_id, begin, end,
                            step_size, directions, means_of_transports, token):

    direction = Direction(channel["sens"])
    means_of_transport = MeansOfTransport(channel["userType"])
    channel_id = channel["id"]

    if direction not in directions:
        return
    if means_of_transport not in means_of_transports:
        return

    samples = apiclient.fetch_channel(domain_id, channel_id, begin, end,
                                      step_size, token)

    if not (means_of_transport, direction) in data:
        data[(means_of_transport, direction)] = samples
    else:
        data[means_of_transport, direction] = \
            _merge_timeseries(data[means_of_transport, direction], samples)


def _merge_timeseries(data1, data2):
    iter1 = iter(data1)
    iter2 = iter(data2)
    merged = []

    sample1 = next(iter1, None)
    sample2 = next(iter2, None)
    while sample1 is not None and sample2 is not None:
        if sample1["date"] == sample2["date"]:
            sample1["comptage"] += sample2["comptage"]
            merged.append(sample1)
            sample1 = next(iter1, None)
            sample2 = next(iter2, None)
        elif sample1["date"] < sample2["date"]:
            merged.append(sample1)
            sample1 = next(iter1, None)
        else:
            merged.append(sample2)
            sample2 = next(iter2, None)

    if sample1 is not None:
        merged.append(sample1)
    if sample2 is not None:
        merged.append(sample2)

    merged.extend(iter1)
    merged.extend(iter2)
    return merged


def _save_data(site_id, data, csv_file):
    for (means_of_transport, direction), samples in data.items():
        for sample in samples:
            row = _map_sample_to_row(site_id, means_of_transport, direction,
                                     sample)
            csv_file.writerow(row)


def _map_sample_to_row(site_id, means_of_transport, direction, sample):
    return {
        Columns.COUNTER_ID: site_id,
        Columns.MEANS_OF_TRANSPORT: means_of_transport,
        Columns.DIRECTION: direction,
        Columns.TIMESTAMP: sample["date"],
        Columns.COUNT: sample["comptage"]
    }
