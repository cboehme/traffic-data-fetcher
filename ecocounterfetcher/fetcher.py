import argparse
import datetime
import textwrap

import requests
from datetime import date

COUNTERS = [
    {"id": 100019809, "name": "5.01 BN - Kennedybrücke (Nordseite)"},
    {"id": 100019810, "name": "5.02 BN - Kennedybrücke (Südseite)"},
    {"id": 100019720, "name": "5.03 BN - Nordbrücke (Südseite)"},
    {"id": 100019721, "name": "5.04 BN - Nordbrücke (Nordseite)"},
    {"id": 100019722, "name": "5.05 BN - Südbrücke (Südseite)"},
    {"id": 100019723, "name": "5.06 BN - Südbrücke (Nordbrücke)"},
    {"id": 100019724, "name": "5.07 BN - Estermannufer"},
    {"id": 100019728, "name": "5.08 BN - Von-Sandt-Ufer"},
    {"id": 100019729, "name": "5.09 BN - Rhenusallee"},
    {"id": 100019725, "name": "5.10 BN - Bröltalbahnweg"},
    {"id": 100019726, "name": "5.11 BN - Brühler Straße"},
    {'id': 100019727, 'name': '5.12 BN - Straßenburger Weg'},  # Guessed ID
    {"id": 100027077, "name": "5.13 BN - Wilhelm-Spiritus-Ufer"},
    {"id": 100027075, "name": "5.14 BN - John-J.-McCloy-Ufer"},
    {"id": 100027076, "name": "5.15 BN - Hochwasserdamm Beuel"},
    {"id": 100053563, "name": "5.16 BN - Joseph-Beuys-Allee"},
    {"id": 100053256, "name": "5.17 BN - Rheinweg"}
]

DIRECTION_BOTH = 0
DIRECTION_IN = 1000000
DIRECTION_OUT = 2000000

STEP_15MIN = 2
STEP_1H = 3
STEP_1D = 4
STEP_7D = 5
STEP_1M = 6

DOMAIN = 4701

# Faking headers is only for "obscurity":
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
}

DATE_FORMAT="%Y%m%d"


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--counter",
                        help="id of the counter to fetch",
                        type=int,
                        choices=range(0, len(COUNTERS)),
                        required=True)
    parser.add_argument("-d", "--direction",
                        help="direction of traffic to fetch",
                        type=str,
                        choices=["in", "out", "both"],
                        default="both")
    parser.add_argument("-g", "--granularity",
                        help="granularity of the data to fetch",
                        type=str,
                        choices=["15min", "hourly", "daily", "weekly", "monthly"],
                        default="hourly")
    parser.add_argument("-f", "-from",
                        help="fetch data starting at date",
                        type=str)
    parser.add_argument("-t", "--to",
                        help="fetch data until date",
                        type=str)
    return parser


def get_counter_info(counter_id: int):
    """
    Gets basic information about a counter such as position,
    starting date of the collection etc.
    """

    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/{counter_id}?withNull=true"

    resp = requests.get(url, headers=HEADERS)
    return resp.json()


def get_counter_token(counter_id: int) -> str:
    """
    Gets ("security") token needed to download the counter’s data.
    You can download once and store them locally since they are static.
    Tokens are individual per counter_id.
    """
    data = get_counter_info(counter_id)
    return data["token"]


def list_counters():
    for (i, counter) in enumerate(COUNTERS):
        print("%i: %s" % (i, counter["name"]))


def show_info():
    # Get counter-id from argv
    # Fetch info
    # Extract interesting values
    parser = init_argparse()
    args = parser.parse_args()
    info = get_counter_info(COUNTERS[args.counter]["id"])
    print(info)


def fetch_data():
    parser = init_argparse()
    args = parser.parse_args()
    counter_id = COUNTERS[args.counter]["id"]
    counter_channel_id = counter_id + DIRECTION_BOTH
    begin_date = None #"20150603"
    end_date = None #"20150603"
    step_size = STEP_15MIN

    counter_info = get_counter_info(counter_id)
    token = counter_info["token"]

    if begin_date is None:
        begin_date = date.fromisoformat(counter_info["date"]).strftime(DATE_FORMAT)
    if end_date is None:
        end_date = date.today().strftime(DATE_FORMAT)

    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/data/{counter_channel_id}?begin={begin_date}&end={end_date}&step={step_size}&domain={DOMAIN}&withNull=true&t={token}"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        print(response.text)
    except Exception as e:
        print(f"An error occured: {e}")


if __name__ == "__main__":
#    fetch_data()
    show_info()
