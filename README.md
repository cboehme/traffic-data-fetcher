# Eco Counter Fetcher

A command line tool for retrieving information about counter sites and fetching 
traffic data from [Eco Counter's](https://www.eco-counter.com/) traffic monitoring stations.

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
## Organisation of the traffic monitoring stations

Eco Counter calls their traffic monitoring stations counter sites. 
A **counter site** groups counters positioned at the same location. 
A **counter** collects data for a specific means of transport and a specific direction of travel.
Each counter site belongs to a domain.
A **domain** groups a number of counter sites which are typically operated by a city or district 
administration.

## Usage

Eco Counter Fetcher supports the commands `list-domains`, `list-sites`, and `fetch-counts`.

By default, the commands write their results to standard output in csv format. By passing a file name
with the `-f` or `--file` option the results can be saved into a csv file.

### List all domains

Retrieves a list of all known domains. As there is no official queryable list of domains, the 
`list-domains` command relies on a list which is regularly updated by a cloud service that checks 
all domain ids between 1 and 10.000 for existing domains.

Usage: `ecocounterfetcher list-domains [-h] [-f FILE]`

Options:
 - `-h`, `--help`: show this help message and exit
 - `-f`, `--file` `FILE`: store domain list in a csv-file. Existing files are overwritten

### List counter sites

Retrieves detailed information for all *public* counter sites within a specified domain, or for the 
provided counter sites.

Usage: `ecocounterfetcher list-sites [-h] (-d DOMAIN_ID | -s SITE_IDS [SITE_IDS ...]) [-f FILE]`

Options:
 - `-h`, `--help`: show this help message and exit
 - `-d`, `--domain` `DOMAIN_ID`: id of the domain whose counter sites should be listed
 - `-s`, `--sites` `SITE_IDS [SITE_IDS ...]`: ids of the counter sites to list
 - `-f`, `--file` `FILE`: store counter sites in a csv-file. Existing files are overwritten

### Fetch counter data

Retrieves traffic data from all counter sites within a specified domain, or from the provided counter sites. 
The returned data can be filtered by means of transport and direction, and constrained by time range and temporal 
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

## Examples
