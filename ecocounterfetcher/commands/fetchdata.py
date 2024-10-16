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


class StepSizeAction(argparse.Action):
    OPTIONS_MAP = {
        "15min": StepSize.QUARTER_OF_AN_HOUR,
        "hourly": StepSize.HOUR,
        "daily": StepSize.DAY,
        "weekly": StepSize.WEEK,
        "monthly": StepSize.MONTH
    }

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.OPTIONS_MAP[values])


def register_argparser(subparsers):
    fetch_parser = subparsers.add_parser("fetch", help='fetch counts')
    fetch_parser.set_defaults(func=fetch_counters)
    fetch_parser.add_argument("-s", "--sites",
                              help="ids of the counter sites to fetch",
                              required=True,
                              dest="site_ids",
                              type=int,
                              action="extend",
                              nargs="+")
    fetch_parser.add_argument("-f", "--file",
                              help="file for storing the fetched data. Data is stored as csv. Existing files are overwritten.",
                              default="-",
                              dest="file",
                              type=argparse.FileType('wt', encoding='UTF-8'))
    fetch_parser.add_argument("-b", "--begin",
                              help="fetch data starting at date",
                              dest="begin",
                              type=str)
    fetch_parser.add_argument("-e", "--end",
                              help="fetch data until date",
                              dest="end",
                              type=str)
    fetch_parser.add_argument("-S", "--step-size",
                              help="step size of the data to fetch",
                              choices=["15min", "hourly", "daily", "weekly",
                                       "monthly"],
                              default=StepSize.HOUR,
                              dest="step_size",
                              type=str,
                              action=StepSizeAction)


def fetch_counters(site_ids, begin, end, step_size, file, **kwargs):
    csv_file = _open_csv(file)
    for site_id in site_ids:
        data = _fetch_all_channels(site_id, begin, end, step_size)
        _save_data(site_id, data, csv_file)


def _open_csv(file):
    csv_file = csv.DictWriter(file, Columns, restval="",
                              extrasaction="ignore", dialect="unix")
    csv_file.writeheader()
    return csv_file


def _fetch_all_channels(site_id, begin, end, step_size):
    site = apiclient.fetch_site(site_id)

    if begin is None:
        begin_date = date.fromisoformat(site["date"])
    else:
        begin_date = date.fromisoformat(begin)
    if end is None:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end)

    domain_id = site["domaine"]
    token = site["token"]
    data = {}
    for channel in site["channels"]:
        fetch_and_merge_channel(data, channel, domain_id, begin_date, end_date,
                                step_size, token)
    return data


def fetch_and_merge_channel(data, channel, domain_id, begin_date, end_date,
                            step_size, token):
    direction = Direction(channel["sens"])
    means_of_transport = MeansOfTransport(channel["userType"])
    channel_id = channel["id"]
    samples = apiclient.fetch_channel(domain_id, channel_id, begin_date,
                                      end_date, step_size, token)
    if not (means_of_transport, direction) in data:
        data[(means_of_transport, direction)] = samples
    else:
        data[means_of_transport, direction] = merge_timeseries(data[means_of_transport, direction], samples)


def merge_timeseries(data1, data2):
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
