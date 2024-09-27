import argparse
import csv
import json
from datetime import date

from ecocounterfetcher.apiclient import get_counter, \
    get_all_counters_in_domain, get_data

STEP_15MIN = 2
STEP_1H = 3
STEP_1D = 4
STEP_7D = 5
STEP_1M = 6

DOMAIN_BONN = 4701


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    list_parser = subparsers.add_parser("list", help="list available counters")

    info_parser = subparsers.add_parser("info", help="print information about a counter")
    info_parser.add_argument("-c", "--counter",
                              help="id of the counter",
                              type=int,
                              required=True)

    fetch_parser = subparsers.add_parser("fetch", help='fetch counts')
    fetch_parser.add_argument("-c", "--counter",
                              help="ids of the counters to fetch",
                              type=int,
                              action="extend",
                              nargs="+",
                              required=True)
    fetch_parser.add_argument("-g", "--granularity",
                              help="granularity of the data to fetch",
                              type=str,
                              choices=["15min", "hourly", "daily", "weekly",
                                       "monthly"],
                              default="hourly")
    fetch_parser.add_argument("-f", "--from",
                              help="fetch data starting at date",
                              type=str)
    fetch_parser.add_argument("-t", "--to",
                              help="fetch data until date",
                              type=str)
    return parser


def list_counters(domain: int):
    counters = get_all_counters_in_domain(domain)
    for counter in counters:
        print("%s: %s" % (counter["idPdc"], counter["nom"]))
    print(json.dumps(counters, indent=4))


def show_counter(args):
    counter = get_counter(args.counter)
    print(json.dumps(counter, indent=4))


def fetch_counters(counter_ids, from_, to, step_size):
    with open("data.csv", "wt", encoding="UTF-8") as file:
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
                "sensor": index + 1,
                "timestamp": sample["date"],
                "count": sample["comptage"]
            }
            csv_file.writerow(row)

def main():
    args = init_argparse().parse_args()
    if args.command == "list":
        list_counters(DOMAIN_BONN)
    elif args.command == "info":
        show_counter(args)
    elif args.command == "fetch":
        granularity_map = {
            "15min": STEP_15MIN,
            "hourly": STEP_1H,
            "daily": STEP_1D,
            "weekly": STEP_7D,
            "monthly": STEP_1M
        }
        step_size = granularity_map[args.granularity]
        fetch_counters(args.counter, args.__dict__["from"], args.to, step_size)


if __name__ == "__main__":
    main()
