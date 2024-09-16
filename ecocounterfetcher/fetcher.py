import argparse
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
    fetch_parser.add_argument("-d", "--direction",
                              help="direction of traffic to fetch",
                              type=str,
                              choices=["a", "b", "both"],
                              default="both")
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


def show_counter(args):
    counter = get_counter(args.counter)
    print(counter)


def fetch_counters(counter_ids, direction, from_, to, step_size):
    for counter_id in counter_ids:
        _fetch_counter(counter_id, direction, from_, to, step_size)


def _fetch_counter(counter_id, direction, from_, to, step_size):
    counter_info = get_counter(counter_id)

    if from_ is None:
        begin_date = date.fromisoformat(counter_info["date"])
    else:
        begin_date = date.fromisoformat(from_)
    if to is None:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(to)

    data = get_data(counter_info, direction, begin_date, end_date, step_size)
    print(data)


def main():
    args = init_argparse().parse_args()
    if args.command == "list":
        list_counters(DOMAIN_BONN)
    elif args.command == "info":
        show_counter(args)
    elif args.command == "fetch":
        direction_map = {
            "a": 0,
            "b": 1,
            "both": -1
        }
        direction = direction_map[args.direction]
        granularity_map = {
            "15min": STEP_15MIN,
            "hourly": STEP_1H,
            "daily": STEP_1D,
            "weekly": STEP_7D,
            "monthly": STEP_1M
        }
        step_size = granularity_map[args.granularity]
        fetch_counters(args.counter, direction, args.__dict__["from"], args.to,
                   step_size)


if __name__ == "__main__":
    main()
