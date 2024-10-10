import argparse
import csv

from ecocounterfetcher.apiclient import get_all_counters_in_domain, get_counter


def register_argparser(subparsers):
    parser = subparsers.add_parser("fetch-sites", help="fetch site infos")
    parser.set_defaults(func=fetch_sites)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain",
                       help="id of the domain whose counter sites should be fetched",
                       dest="domain_id",
                       type=int)
    group.add_argument("-s", "--sites",
                       help="ids of the counter sites to fetch",
                       dest="site_ids",
                       type=int,
                       action="extend",
                       nargs="+")
    parser.add_argument("-f", "--file",
                        help="file for storing the fetched data. Data is stored as csv. Existing files are overwritten.",
                        default="-",
                        dest="file",
                        type=argparse.FileType('wt', encoding='UTF-8'))


def fetch_sites(domain_id, site_ids, file, **kwargs):
    if domain_id is not None:
        site_ids = _fetch_sites_in_domain(domain_id)
    csv_file = _open_csv(file, [
        "id",
        "domain_id",
        "name",
        "latitude",
        "longitude",
        "direction_in",
        "direction_out",
        "means_of_transport_count",
        "main_means_of_transport",
        "start_of_collection",
        "message"
    ])
    csv_file.writeheader()
    for site_id in site_ids:
        site = get_counter(site_id)
        row = {
            "id": site["idPdc"],
            "domain_id": site["domaine"],
            "name": site["titre"],
            "latitude": site["latitude"],
            "longitude": site["longitude"],
            "direction_in": site["directionIn"],
            "direction_out": site["directionOut"],
            "means_of_transport_count": site["nbPratiques"],
            "main_means_of_transport": site["pratique"],
            "start_of_collection": site["date"],
            "message": site["message"]
        }
        csv_file.writerow(row)


def _open_csv(file, field_names):
    return csv.DictWriter(file, field_names, restval="",
                          extrasaction="ignore", dialect="unix")


def _fetch_sites_in_domain(domain_id):
    sites = get_all_counters_in_domain(domain_id)
    return [site["idPdc"] for site in sites]
