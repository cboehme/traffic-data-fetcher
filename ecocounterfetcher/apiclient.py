from datetime import date
from enum import Enum

import requests


# Faking headers is only for "obscurity":
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
}

DATE_FORMAT="%Y%m%d"


class Step(Enum):
    QUARTER_OF_AN_HOUR = 2
    HOUR = 3
    DAY = 4
    WEEK = 5
    MONTH = 6


def get_all_counters_in_domain(domain: int):
    """
    Retrieves a list of all available counters in the given domain.
    """
    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpageplus/{domain}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_counter(counter_id: int):
    """
    Gets basic information about a counter such as its position,
    starting date of the collection, etc.
    """
    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/{counter_id}?withNull=true"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def get_data(counter, channel_no: int, begin: date, end: date, step_size: Step):
    """
    Gets the data collected by a counter in a given time range.
    """
    channel_id = counter["channels"][channel_no]["id"]
    domain = counter["domaine"]
    token = counter["token"]

    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/data/{channel_id}?begin={begin.strftime(DATE_FORMAT)}&end={end.strftime(DATE_FORMAT)}&step={step_size.value}&domain={domain}&withNull=true&t={token}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
