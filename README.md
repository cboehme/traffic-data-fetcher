# Eco Counter Fetcher

A command line tool for fetching data from [Eco Counter's](https://www.eco-counter.com/) traffic counters.

## Installation

Eco Counter Fetcher requires Python 3.8 or higher. 
The recommended way to install Eco Counter Fetcher is via [pipx](https://pipx.pypa.io/):
```shell
python3 -m pipx install ecocounterfetcher
```
Alternatively, pipx allows to directly run Eco Counter Fetcher without installing it first:
```shell
python3 -m pipx run ecoounterfetcher YOUR-ARGS-HERE
```

## Usage

Eco Counter Fetcher can 
 - list all domains,
 - list information about counter sites,
 - or fetch data from counters.

All commands support the `--file` or `-f` argument to specify a file for storing the fetched data in csv 
format.

When calling `fetch-sites` or `fetch-counts` the sites which should be fetched must be specified either by
passing a list of site ids with the `--sites` or `-s` argument, or by giving a domain id with 
the `--domain` or `-d` argument.

### List all domains

Retrieve a list of all known domains.

Usage: `ecocounterfetcher fetch-domains [-h] [-f FILE]`

Options:
 - `-h`, `--help`: show this help message and exit
 - `-f`, `--file` `FILE`: store domain list in a csv-file. Existing files are overwritten

### List counter sites

Retrieve detailed information for all counter sites within a specified domain, or from the provided counter sites.

Usage: `ecocounterfetcher fetch-sites [-h] (-d DOMAIN_ID | -s SITE_IDS [SITE_IDS ...]) [-f FILE]`

Options:
 - `-h`, `--help`: show this help message and exit
 - `-d`, `--domain` `DOMAIN_ID`: id of the domain whose conuter sites should be fetched
 - `-s`, `--sites` `SITE_IDS [SITE_IDS ...]`: ids of the counter sites to fetch
 - `-f`, `--file` `FILE`: store counter sites in a csv-file. Existing files are overwritten

### Fetch counter data

Retrieve traffic data from all counter sites within a specified domain, or from the provided counter sites. 
The returned data can be filtered by transport mode and direction, and constrained by time range and temporal 
resolution.

Usage: 
```
ecocounterfetcher fetch-counts [-h] (-d DOMAIN_ID | -s SITE_IDS [SITE_IDS ...]) 
                               [-f FILE] 
                               [-S {quarter_of_an_hour,hour,day,week,month}]
                               [-B BEGIN] [-E END] 
                               [-D {in,out,none} [{in,out,none} ...]]
                               [-M {foot,bike,horse,car,bus,minibus,undefined,motorcycle,kayak,e_scooter,truck} 
                                  [{foot,bike,horse,car,bus,minibus,undefined,motorcycle,kayak,e_scooter,truck} 
                                  ...]]`
```

Options:
 - `-h`, `--help`: show this help message and exit
 - `-d`, `--domain` `DOMAIN_ID`: id of the domain whose counter sites should be fetched
 - `-s`, `--sites` `SITE_IDS [SITE_IDS ...]`: ids of the counter sites to fetch
 - `-f`, `--file` `FILE`: store data in a csv-file. Existing files are overwritten
 - `-S`, `--step-size {quarter_of_an_hour,hour,day,week,month}`: step size of the data to fetch
 - `-B`, `--begin BEGIN`: fetch data starting at date. Date must be ISO 8610 formatted (YYYY-MM-DD)
 - `-E`, `--end END`: fetch data until date (exclusively). Date must be ISO 8610 formatted (YYYY-MM-DD)
 - `-D`, `--direction {in,out,none} [{in,out,none} ...]`: select directions to fetch
 - `-M`, `--means-of-transport {foot,bike,horse,car,bus,minibus,undefined,motorcycle,kayak,e_scooter,truck} [{foot,bike,horse,car,bus,minibus,undefined,motorcycle,kayak,e_scooter,truck} ...]`: select means of transport to fetch
