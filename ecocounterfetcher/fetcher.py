import argparse
import csv
import json
from datetime import date

from ecocounterfetcher.apiclient import get_counter, \
    get_all_counters_in_domain, get_data, Step

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


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    list_parser = subparsers.add_parser("list", help="list available counters")
    list_parser.set_defaults(func=list_counters)
    list_parser.add_argument("-d", "--domain",
                             help="id of the domain",
                             required=True,
                             dest="domain_id",
                             type=int)

    info_parser = subparsers.add_parser("info", help="print information about a counter")
    info_parser.set_defaults(func=show_counter)
    info_parser.add_argument("-c", "--counter",
                             help="id of the counter",
                             required=True,
                             dest="counter_id",
                             type=int)

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
                              required=True,
                              dest="filename",
                              type=str)
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
    return parser


def list_counters(domain_id, **kwargs):
    counters = get_all_counters_in_domain(domain_id)
    for counter in counters:
        print("%s: %s" % (counter["idPdc"], counter["nom"]))
    print(json.dumps(counters, indent=4))


def show_counter(counter_id, **kwargs):
    counter = get_counter(counter_id)
    print(json.dumps(counter, indent=4))


def fetch_counters(counter_ids, from_, to, step_size, filename, **kwargs):
    with open(filename, "wt", encoding="UTF-8") as file:
        csv_file = _open_csv(file, ["counter_id", "sensor_no", "timestamp", "count"])
        csv_file.writeheader()
        for counter_id in counter_ids:
            _fetch_counter(counter_id, from_, to, step_size, csv_file)


def _open_csv(file, field_names):
    return csv.DictWriter(file, field_names, restval="",
                          extrasaction="ignore", dialect="unix")


def _fetch_counter(counter_id, from_, to, step_size, csv_file):
    counter = get_counter(counter_id)

    if from_ is None:
        begin_date = date.fromisoformat(counter["date"])
    else:
        begin_date = date.fromisoformat(from_)
    if to is None:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(to)

    data_per_sensor = [None] * counter["nbSens"]
    for channel_no, channel in enumerate(counter["channels"]):
        sensor_no = channel["sens"] - 1
        data = get_data(counter, channel_no, begin_date, end_date, step_size)
        if data_per_sensor[sensor_no] is None:
            data_per_sensor[sensor_no] = data
        else:
            for sample_accumulated, sample in zip(data_per_sensor[sensor_no], data):
                if sample_accumulated["date"] != sample["date"]:
                    print("Warning: Timestamps do not match. This should not happen")
                else:
                    sample_accumulated["comptage"] += sample["comptage"]
    _save_data(counter_id, data_per_sensor, csv_file)


def _save_data(counter_id, data_per_sensor, csv_file):
    for index, data in enumerate(data_per_sensor):
        for sample in data:
            row = {
                "counter_id": counter_id,
                "sensor_no": index + 1,
                "timestamp": sample["date"],
                "count": sample["comptage"]
            }
            csv_file.writerow(row)


def main():
    args = init_argparse().parse_args()
    if hasattr(args, "func"):
        args.func(**vars(args))


if __name__ == "__main__":
    main()
