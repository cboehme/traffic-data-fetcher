# Traffic Data Fetcher - Retrieve data from Eco Counter's traffic counter API
# Copyright (C) 2025  Christoph Böhne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
from importlib.metadata import PackageNotFoundError, version

from trafficdatafetcher.commands import listsites, fetchcounts, listdomains


def get_version() -> str:
    try:
        return version("traffic-data-fetcher")
    except PackageNotFoundError:
        return "unknown"

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {get_version()}')
    subparsers = parser.add_subparsers(required=True)

    listdomains.register_argparser(subparsers)
    listsites.register_argparser(subparsers)
    fetchcounts.register_argparser(subparsers)

    return parser

def main():
    args = init_argparse().parse_args()
    if hasattr(args, "func"):
        args.func(**vars(args))


if __name__ == "__main__":
    main()
