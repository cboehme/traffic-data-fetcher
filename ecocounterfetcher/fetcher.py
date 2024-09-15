import argparse
from datetime import date

import requests

DIRECTION_BOTH = 0
DIRECTION_IN = 1000000
DIRECTION_OUT = 2000000

STEP_15MIN = 2
STEP_1H = 3
STEP_1D = 4
STEP_7D = 5
STEP_1M = 6

DOMAIN_BONN = 4701

# Faking headers is only for "obscurity":
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
}

DATE_FORMAT="%Y%m%d"


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
                              #action="extend",
                              #nargs="+",
                              required=True)
    fetch_parser.add_argument("-d", "--direction",
                              help="direction of traffic to fetch",
                              type=str,
                              choices=["in", "out", "both"],
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


def get_counter_info(counter_id: int):
    """
    Gets basic information about a counter such as its position,
    starting date of the collection, etc.
    """

    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/{counter_id}?withNull=true"

    resp = requests.get(url, headers=HEADERS)
    return resp.json()


def list_counters(domain: int):
    """
    Retrieves a list of all available counters in the given domain.
    """

    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpageplus/{domain}"

    resp = requests.get(url, headers=HEADERS)
    counters = resp.json()
    for counter in counters:
        print("%s: %s" % (counter["idPdc"], counter["nom"]))


def show_info(args):
    info = get_counter_info(args.counter)
    print(info)


def fetch_data(counter_id, direction, begin_date, end_date, step_size):
    counter_channel_id = counter_id + direction

    counter_info = get_counter_info(counter_id)
    token = counter_info["token"]
    domain = counter_info["domaine"]

    if begin_date is None:
        begin_date = date.fromisoformat(counter_info["date"]).strftime(DATE_FORMAT)
    if end_date is None:
        end_date = date.today().strftime(DATE_FORMAT)

    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/data/{counter_channel_id}?begin={begin_date}&end={end_date}&step={step_size}&domain={domain}&withNull=true&t={token}"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    args = init_argparse().parse_args()
    if args.command == "list":
        list_counters(DOMAIN_BONN)
    elif args.command == "info":
        show_info(args)
    elif args.command == "fetch":
        direction_map = {
            "in": DIRECTION_IN,
            "out": DIRECTION_OUT,
            "both": DIRECTION_BOTH
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
        fetch_data(args.counter, direction, args.__dict__["from"], args.to,
                   step_size)


if __name__ == "__main__":
    main()
