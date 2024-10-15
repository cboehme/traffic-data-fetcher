import argparse
import csv
from datetime import date
from enum import auto

from ecocounterfetcher import apiclient
from ecocounterfetcher.apiclient import Step, Direction, MeansOfTransport
from ecocounterfetcher.types import EnumWithLowerCaseNames


class Columns(EnumWithLowerCaseNames):
    COUNTER_ID = auto()
    MEANS_OF_TRANSPORT = auto()
    DIRECTION = auto()
    TIMESTAMP = auto()
    COUNT = auto()


class GranularityAction(argparse.Action):
    GRANULARITY_MAP = {
        "15min": Step.QUARTER_OF_AN_HOUR,
        "hourly": Step.HOUR,
        "daily": Step.DAY,
        "weekly": Step.WEEK,
        "monthly": Step.MONTH
    }

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.GRANULARITY_MAP[values])


def register_argparser(subparsers):
    fetch_parser = subparsers.add_parser("fetch", help='fetch counts')
    fetch_parser.set_defaults(func=fetch_counters)
    fetch_parser.add_argument("-c", "--counter",
                              help="ids of the counters to fetch",
                              required=True,
                              dest="counter_ids",
                              type=int,
                              action="extend",
                              nargs="+")
    fetch_parser.add_argument("-F", "--file",
                              help="file for storing the fetched data. Data is stored as csv. Existing files are overwritten.",
                              default="-",
                              dest="file",
                              type=argparse.FileType('wt', encoding='UTF-8'))
    fetch_parser.add_argument("-f", "--from",
                              help="fetch data starting at date",
                              dest="from_",
                              type=str)
    fetch_parser.add_argument("-t", "--to",
                              help="fetch data until date",
                              dest="to",
                              type=str)
    fetch_parser.add_argument("-g", "--granularity",
                              help="granularity of the data to fetch",
                              choices=["15min", "hourly", "daily", "weekly",
                                       "monthly"],
                              default=Step.HOUR,
                              dest="step_size",
                              type=str,
                              action=GranularityAction)

def fetch_counters(counter_ids, from_, to, step_size, file, **kwargs):
    csv_file = _open_csv(file)
    for counter_id in counter_ids:
        data = _fetch_counter(counter_id, from_, to, step_size)
        _save_data(counter_id, data, csv_file)


def _open_csv(file):
    csv_file = csv.DictWriter(file, Columns, restval="",
                              extrasaction="ignore", dialect="unix")
    csv_file.writeheader()
    return csv_file


def _fetch_counter(counter_id, from_, to, step_size):
    site = apiclient.fetch_site(counter_id)

    if from_ is None:
        begin_date = date.fromisoformat(site["date"])
    else:
        begin_date = date.fromisoformat(from_)
    if to is None:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(to)

    domain_id = site["domaine"]
    token = site["token"]
    data = {}
    for channel in site["channels"]:
        direction = Direction(channel["sens"])
        means_of_transport = MeansOfTransport(channel["userType"])
        channel_id = channel["id"]
        samples = apiclient.get_data(domain_id, channel_id, begin_date, end_date, step_size, token)
        if not (means_of_transport, direction) in data:
            data[(means_of_transport, direction)] = samples
        else:
            for sample_accumulated, sample in zip(data[(means_of_transport, direction)], samples):
                if sample_accumulated["date"] != sample["date"]:
                    print("Warning: Timestamps do not match. This should not happen")
                else:
                    sample_accumulated["comptage"] += sample["comptage"]
    return data


def _save_data(counter_id, data, csv_file):
    for (means_of_transport, direction), samples in data.items():
        for sample in samples:
            row = {
                Columns.COUNTER_ID: counter_id,
                Columns.MEANS_OF_TRANSPORT: means_of_transport,
                Columns.DIRECTION: direction,
                Columns.TIMESTAMP: sample["date"],
                Columns.COUNT: sample["comptage"]
            }
            csv_file.writerow(row)
