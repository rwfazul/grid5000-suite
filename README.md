# grid5000-suite

## g5.py

A simple wrapper for the GRID'5000 RESTful API that allows OAR reservations and job management. 

## Requirements

- Python 3+
- Requests library

```bash
	$ pip install requests
```

## Configuration

- Add the following entry in the ~/.netrc file:

```
	machine api.grid5000.fr
	login <your-grid5000-login>
	password <your-grid5000-password>
```

- If you have to create the .netrc file, also run the following command:

```bash
	$ chmod 600 ~/.netrc
```

## Usage

```
usage: g5.py [-h] [--list_sites] [--list_clusters SITE_NAME]
             [--list_nodes SITE_NAME CLUSTER_NAME] [--site_status SITE_NAME]
             [--verbose] [--grid_status] [--sub SITE_NAME]
             [--cancel SITE_NAME JOB_ID]

A simple Python wrapper for GRID'5000 RESTful API

optional arguments:
  -h, --help            show this help message and exit
  --list_sites          list all GRID'5000 sites
  --list_clusters SITE_NAME
                        list all clusters in the given site
  --list_nodes SITE_NAME CLUSTER_NAME
                        list all nodes in the given site and cluster
  --site_status SITE_NAME
                        print the status of the given site
  --verbose, -v         verbose output
  --grid_status         print GRID'5000 status (available nodes on each site)
  --sub SITE_NAME       make a reservation in the given site
  --cancel SITE_NAME JOB_ID
                        cancel a reservation or delete a job
```

## experiments

In the experiments folder you will find some useful shell scripts to Hadoop build and benchmarks on GRID'5000 (w/ hg5k project).
