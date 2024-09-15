from datetime import date

import requests


# Faking headers is only for "obscurity":
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
}

DATE_FORMAT="%Y%m%d"

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


def get_data(counter, channel: int, begin_date: date, end_date: date, step_size: int):
    """
    Gets the data collected by a counter in a given time range.
    """
    if 0 <= channel < len(counter["channels"]):
        counter_channel_id = counter["channels"][channel][id]
    else:
        counter_channel_id = counter["idPdc"]
    domain = counter["domaine"]
    token = counter["token"]

    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/data/{counter_channel_id}?begin={begin_date.strftime(DATE_FORMAT)}&end={end_date.strftime(DATE_FORMAT)}&step={step_size}&domain={domain}&withNull=true&t={token}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

