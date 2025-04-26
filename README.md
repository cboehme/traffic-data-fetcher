# Traffic Data Fetcher

A command line tool for retrieving information about counter sites and retrieving 
traffic data from [Eco Counter's](https://www.eco-counter.com/) traffic monitoring stations.

## Installation

Traffic Data Fetcher requires Python 3.8 or higher. 
The recommended way to install Traffic Data Fetcher is via [pipx](https://pipx.pypa.io/):
```shell
python3 -m pipx install traffic-data-fetcher
```
Alternatively, pipx allows directly running Traffic Data Fetcher without installing it first:
```shell
python3 -m pipx run traffic-data-fetcher YOUR-ARGS-HERE
```

## Organisation of the traffic monitoring stations

Eco Counter calls their traffic monitoring stations counter sites. 
A **counter site** groups counters positioned at the same location. 
A **counter** collects data for a specific means of transport and a specific direction of travel.
Each counter site belongs to a domain.
A **domain** groups a number of counter sites which are typically operated by a city or district 
administration.

A counter site may be either *public* or *non-public*. Detailed traffic data separated by 
direction is only available for public sites. Traffic Data Fetcher currently does not support 
fetching data from non-public sites.

## Usage

Traffic Data Fetcher supports the commands `list-domains`, `list-sites`, and `fetch-counts`.

By default, the commands write their results to standard output in csv format. By passing a file name
with the `-f` or `--file` option the results can be saved into a csv file.

Standard options:
 - `-h`, `--help`: show a help message and exit
 - `--version`: show the version of traffic-data-fetcher and exit

### List all domains

Retrieves a list of all known domains. As there is no official queryable list of domains, the 
`list-domains` command relies on a list which is regularly updated by a cloud service that checks 
all domain ids between 1 and 10.000 for existing domains.

Usage: `traffic-data-fetcher list-domains [-h] [-f FILE]`

Options:
 - `-h`, `--help`: show a help message and exit
 - `-f`, `--file` `FILE`: store a domain list in a csv-file. Existing files are overwritten

### List counter sites

Retrieves detailed information for all (*public* and *non-public*) counter sites within a specified 
domain, or for the provided counter sites. If individual counter sites are queried, only *public* 
sites can be retrieved.

Usage: `traffic-data-fetcher list-sites [-h] (-d DOMAIN_ID | -s SITE_IDS [SITE_IDS ...]) [-f FILE]`

Options:
 - `-h`, `--help`: show a help message and exit
 - `-d`, `--domain` `DOMAIN_ID`: id of the domain whose counter sites should be listed
 - `-s`, `--sites` `SITE_IDS [SITE_IDS ...]`: ids of the counter sites to list
 - `-f`, `--file` `FILE`: store counter sites in a csv-file. Existing files are overwritten

### Fetch counter data

Retrieves traffic data from all *public* counter sites within a specified domain or from the provided *public* 
counter sites. 
The returned data can be filtered by means of transport and direction, and constrained by time range and temporal 
resolution.

Usage: 
```
traffic-data-fetcher fetch-counts [-h] (-d DOMAIN_ID | -s SITE_IDS [SITE_IDS ...]) 
                                  [-f FILE] 
                                  [-S {quarter_of_an_hour,hour,day,week,month}]
                                  [-B BEGIN] [-E END] 
                                  [-D {in,out,none} [{in,out,none} ...]]
                                  [-M {foot,bike,horse,car,bus,minibus,undefined,motorcycle,kayak,e_scooter,truck} 
                                      [{foot,bike,horse,car,bus,minibus,undefined,motorcycle,kayak,e_scooter,truck} 
                                      ...]]`
```

Options:
 - `-h`, `--help`: show a help message and exit
 - `-d`, `--domain` `DOMAIN_ID`: id of the domain whose counter sites should be fetched
 - `-s`, `--sites` `SITE_IDS [SITE_IDS ...]`: ids of the counter sites to fetch
 - `-f`, `--file` `FILE`: store data in a csv-file. Existing files are overwritten
 - `-S`, `--step-size {quarter_of_an_hour,hour,day,week,month}`: step size of the data to fetch. Defaults to `hour`
 - `-B`, `--begin BEGIN`: fetch data starting at date. Date must be ISO 8610 formatted (YYYY-MM-DD)
 - `-E`, `--end END`: fetch data until date (exclusively). Date must be ISO 8610 formatted (YYYY-MM-DD)
 - `-D`, `--direction {in,out,none} [{in,out,none} ...]`: select directions to fetch. By default, data for all directions is fetched
 - `-M`, `--means-of-transport {foot,bike,horse,car,bus,minibus,undefined,motorcycle,kayak,e_scooter,truck} [{foot,bike,horse,car,bus,minibus,undefined,motorcycle,kayak,e_scooter,truck} ...]`: select means of transport to fetch. By default, data for all means of transport is fetched

## Examples

- Show the list of known domains:
  ```shell
  traffic-data-fetcher list-domains
  ```
- Show details for all counter sites in the domain *Stadt Bonn*:
  ```shell
  traffic-data-fetcher list-sites --domain 4701
  ```
`- Retrieve the monthly count data for all counters at the two counter sites *Kennedybrücke (Nordseite)* and 
  *Kennedybrücke (Südseite)* in Bonn:`
  ```shell
  traffic-data-fetcher fetch-counts --sites 100019809,100019810 --step-size month
  ```
- Retrieve the monthly count data for cars entering Ludwigsburg via Bismarckstraße (the counter 
  site records counts for both bicycles and cars):
  ```shell
  # Get the details of the counter site to find out 
  # which direction corresponds to going into town:
  traffic-data-fetcher list-sites --sites 300015617
  # Going into town is represented by direction in (unsurprisingly).
  # Using this information the data can be fetched like this:
  traffic-data-fetcher fetch-counts --sites 300015617 --step-size month --direction IN --means-of-transport car
  ```
- Retrieve hourly count data per recorded at the counter site *Rhenusallee* in Bonn for the dates Saturday, April 5, 2025, 
  and Sunday, April 6, 2025:
  ```shell
  traffic-data-fetcher fetch-counts --sites 100019729 --begin 2025-04-05 --end 2025-04-07
  ```
  
## Acknowledgements

Special thanks to Pascua Theus for providing the groundwork for accessing Eco Counter's API in
his [blog post on counting bicycles](https://theus.name/2019/06/01/fahrraeder-zaehlen/) and to
the [Bundesstelle for Open Data](https://github.com/bundesAPI) for their documentation of
the [Eco-Visio-API](https://github.com/bundesAPI/eco-visio-api).
Their contributions were essential to making this project possible.