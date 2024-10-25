import argparse
import csv

from ecocounterfetcher import apiclient


def positive_value(value):
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return int_value


def fetch_site_ids_for_domain(domain_id):
    sites = apiclient.fetch_sites_in_domain(domain_id)
    return [site["lienPublic"]for site in sites if site["lienPublic"] is not None]


def open_csv(file, columns):
    csv_file = csv.DictWriter(file, columns, restval="",
                              extrasaction="ignore", dialect="unix")
    csv_file.writeheader()
    return csv_file
