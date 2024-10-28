from datetime import date

import requests

from ecocounterfetcher.types import EnumWithLowerCaseNames

# Faking headers is only for "obscurity":
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
}

DATE_FORMAT="%Y%m%d"


class StepSize(EnumWithLowerCaseNames):
    QUARTER_OF_AN_HOUR = 2
    HOUR = 3
    DAY = 4
    WEEK = 5
    MONTH = 6


class Direction(EnumWithLowerCaseNames):
    IN = 1
    OUT = 2
    NONE = 5


class MeansOfTransport(EnumWithLowerCaseNames):
    FOOT = 1
    BIKE = 2
    HORSE = 3
    CAR = 4
    BUS = 5
    MINIBUS = 6
    UNDEFINED = 7
    MOTORCYCLE = 8
    KAYAK = 9
    E_SCOOTER = 13
    TRUCK = 14


def fetch_domains():
    """
    Retrieves a list of all known domains.
    """
    url = "https://gist.githubusercontent.com/cboehme/5034712e9e86452d9197998b2837fc76/raw/cfad2357fae1ba409980337edfb78a642dd276ce/domains.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred while fetching domains: {e}")
        return []


def fetch_sites_in_domain(domain_id: int):
    """
    Retrieves a list of all available counter sites in the given domain.
    """
    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpageplus/{domain_id}?withNull=true"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def fetch_site(site_id: int):
    """
    Gets basic information about a counter site such as its position,
    starting date of the collection, etc.
    """
    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/{site_id}?withNull=true"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def fetch_channel(domain_id: int, channel_id: int, begin: date, end: date, step_size: StepSize, token: str):
    """
    Gets the data collected in a channel at counter site in a given time range.
    """
    begin_param = f"&begin={begin.strftime(DATE_FORMAT)}" if begin is not None else ""
    end_param = f"&end={end.strftime(DATE_FORMAT)}" if end is not None else ""
    url = f"https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/data/{channel_id}?step={step_size.value}&domain={domain_id}{begin_param}{end_param}&withNull=true&t={token}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
