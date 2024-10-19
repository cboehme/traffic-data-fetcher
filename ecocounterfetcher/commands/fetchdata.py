import argparse
import csv
from datetime import date
from enum import auto

from ecocounterfetcher import apiclient
from ecocounterfetcher.apiclient import StepSize, Direction, MeansOfTransport
from ecocounterfetcher.types import EnumWithLowerCaseNames


class Columns(EnumWithLowerCaseNames):
    COUNTER_ID = auto()
    MEANS_OF_TRANSPORT = auto()
    DIRECTION = auto()
    TIMESTAMP = auto()
    COUNT = auto()


STEP_SIZES = {
    "15min": StepSize.QUARTER_OF_AN_HOUR,
    "hourly": StepSize.HOUR,
    "daily": StepSize.DAY,
    "weekly": StepSize.WEEK,
    "monthly": StepSize.MONTH
}

DIRECTIONS = {
    "in": Direction.IN,
    "out": Direction.OUT,
    "none": Direction.NONE
}

MEANS_OF_TRANSPORT = {
    "foot": MeansOfTransport.FOOT,
    "bike": MeansOfTransport.BIKE,
    "horse": MeansOfTransport.HORSE,
    "car": MeansOfTransport.CAR,
    "bus": MeansOfTransport.BUS,
    "minibus": MeansOfTransport.MINIBUS,
    "undefined": MeansOfTransport.UNDEFINED,
    "motorcycle": MeansOfTransport.MOTORCYCLE,
    "kayak": MeansOfTransport.KAYAK,
    "e-scooter": MeansOfTransport.E_SCOOTER,
    "truck": MeansOfTransport.TRUCK
}

def register_argparser(subparsers):
    parser = subparsers.add_parser("fetch", help='fetch counts')
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
    parser.add_argument("-S", "--step-size",
                        help="step size of the data to fetch",
                        choices=STEP_SIZES.values(),
                        default=StepSize.HOUR,
                        dest="step_size",
                        type=STEP_SIZES.get)
    parser.add_argument("-f", "--file",
                        help="file for storing the fetched data. Data is stored as csv. Existing files are overwritten.",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))
    parser.add_argument("-B", "--begin",
                        help="fetch data starting at date",
                        dest="begin",
                        type=date.fromisoformat)
    parser.add_argument("-E", "--end",
                        help="fetch data until date",
                         dest="end",
                        type=date.fromisoformat)
    parser.add_argument("-D", "--direction",
                        help="select directions to fetch",
                        choices=DIRECTIONS.values(),
                        default=list(Direction),
                        dest="direction",
                        type=DIRECTIONS.get,
                        nargs="+")
    parser.add_argument("-M", "--means-of-transport",
                        help="select means of transport to fetch",
                        choices=MEANS_OF_TRANSPORT.values(),
                        default=list(MeansOfTransport),
                        dest="means_of_transport",
                        type=MEANS_OF_TRANSPORT.get,
                        nargs="+")


def fetch_data(domain_id, site_ids, step_size, file, begin, end, direction, means_of_transport, **kwargs):
    if domain_id is not None:
        site_ids = _fetch_site_ids_for_domain(domain_id)

    csv_file = _open_csv(file)
    for site_id in site_ids:
        data = _fetch_all_channels(step_size, site_id, begin, end, direction, means_of_transport)
        _save_data(site_id, data, csv_file)


def _fetch_site_ids_for_domain(domain_id):
    sites = apiclient.fetch_sites_in_domain(domain_id)
    return [site["idPdc"] for site in sites]


def _open_csv(file):
    csv_file = csv.DictWriter(file, Columns, restval="",
                              extrasaction="ignore", dialect="unix")
    csv_file.writeheader()
    return csv_file


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

    try:
        sample1 = next(iter1)
        sample2 = next(iter2)

        while True:
            if sample1["date"] == sample2["date"]:
                sample1["comptage"] += sample2["comptage"]
                merged.append(sample1)
                sample1 = next(iter1)
                sample2 = next(iter2)
            elif sample1["date"] < sample2["date"]:
                merged.append(sample1)
                sample1 = next(iter1)
            else:
                merged.append(sample2)
                sample2 = next(iter2)
    except StopIteration:
        pass
    # Append any remaining items from either iterator:
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
