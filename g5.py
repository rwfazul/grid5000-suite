#!/usr/bin/env python3

import json
import requests
import sys
import argparse

def api(subpath, r_type='get', headers=None, data=None):
    API_URL = 'https://api.grid5000.fr/3.0/'
    try:
        response = None
        if r_type is 'post':
            response = requests.post('{}{}'.format(API_URL, subpath), headers=headers, data=json.dumps(data))
        elif r_type is 'delete':
            response = requests.delete('{}{}'.format(API_URL, subpath))
        else:
            response = requests.get('{}{}'.format(API_URL, subpath))
        if response.status_code == 401:
            print('* error: unauthorized access')
            print('\t** create or check the ~/.netrc file. it should contains the following entry:')
            print('\t\tmachine api.grid5000.fr')
            print('\t\tlogin <your-grid5000-login>')
            print('\t\tpassword <your-grid5000-password>')
            print('\t** if you have to create the .netrc file, also run the following command: $ chmod 600 ~/.netrc ')
            sys.exit(1)
        if r_type is 'get':
            return json.loads(response.text)
        return response
    except Exception as e:
        print('* error: check your internet connection')
        print(e)
        sys.exit(1)

def list_sites(sites_list=False):
    response = api('sites')
    sites=[]
    for site in response.get('items'):
        sites.append(site.get('name'))
    sites = [s.split('-')[0] for s in sites] 
    sites = [s.lower() for s in sites]
    if sites_list:
        return sites
    print("available sites: {}".format(sites))

def list_site_clusters(site, clusters_list=False):
    response = api('sites/{}/clusters'.format(site.lower()))
    clusters=[]
    for cluster in response.get('items'):
        clusters.append(cluster.get('uid'))
    if clusters_list:
        return clusters
    print("available clusters in {}: {}".format(site, clusters))

def list_cluster_nodes(site, cluster):
    response = api('sites/{}/clusters/{}/nodes'.format(site.lower(), cluster.lower()))
    print('available nodes in {}|{} (total={}):'.format(site, cluster, response.get('total')))
    for node in response.get('items'):
        for node_adapter in node.get('network_adapters'):
            if node_adapter.get('ip') is not None:
                print('\t{}: {}'.format(node_adapter.get('ip'), node_adapter.get('network_address')))
                break

def check_site_status(site, verbose=True):
    dict_hard = {
        "dead": "node is dead", 
        "alive": "node is running", 
        "standby": "node is shutdown to reduce power consumption, but available for jobs", 
        "absent": "node is probably rebooting", 
        "suspected": "unknown state"
    }
    dict_soft = {
        "unknown": "node is dead or suspected",
        "free": "no job currently running on the node",
        "busy": "job is running on this node",
        "besteffort": "a besteffort job is running in the node"
    }
    response = api('sites/{}/status'.format(site.lower()))
    print('status of site {} (total nodes={})'.format(site, len(response.get('nodes'))))
    free_nodes = []
    for k,v in response.get('nodes').items():
        if verbose:
            print('\tnode: {}'.format(k))
            print('\t\thardware status: {} ({})'.format(v.get('hard'), dict_hard.get(v.get('hard'))))
            print('\t\tsoftware status: {} ({})'.format(v.get('soft'), dict_soft.get(v.get('soft'))))
            reservations_waiting = 0
            reservations_running = 0
            for r in v.get('reservations'):
                if r.get('state') is 'waiting':
                    reservations_waiting = reservations_waiting + 1
                elif r.get('state') is 'running':
                    reservations_running = reservations_running + 1
            print('\t\tnumber of reservations: {} (waiting={}, running={})'.format(len(v.get('reservations')), reservations_waiting, reservations_running))
        if v.get('soft').strip() == 'free' or v.get('soft').strip() == 'unknown':
            free_nodes.append(format(k))
    print('*** free nodes founded on site {} (total={})'.format(site, len(free_nodes)))
    if verbose:
        for node in free_nodes:
            print('\t{}'.format(node))

def check_grid_status():
    for site in list_sites(sites_list=True):
        response = api('sites/{}/status'.format(site.lower()))
        besteffort_nodes = 0
        busy_nodes = 0
        for node in response.get('nodes').values():
            if node.get('soft').strip() == 'busy':
                busy_nodes = busy_nodes + 1
            elif node.get('soft').strip() == 'besteffort':
                besteffort_nodes = besteffort_nodes + 1
        total_nodes = len(response.get('nodes'))
        busy_nodes = busy_nodes + besteffort_nodes
        free_nodes = total_nodes - busy_nodes
        print('site {}: total_nodes={}, busy_nodes={}, free_nodes={}'.format(site.lower(), total_nodes, busy_nodes, free_nodes))

def make_reservation(site):
    sites = list_sites(sites_list=True)
    assert site in sites, "* error: {} is not an available site ({})".format(site, sites)
    raw_data = get_parameters(site)
    data = { "command": raw_data['command'] }
    if raw_data.get('start_at'):
        data['reservation'] = raw_data['start_at']
    resources = 'nodes={}, walltime={}'.format(raw_data['num_nodes'], raw_data['walltime'])
    if raw_data.get('cluster'):
        data['properties'] = "cluster='{}'".format(raw_data['cluster'])
    elif raw_data.get('num_clusters'):
        resources = 'cluster={}/{}'.format(raw_data['num_clusters'], resources)
    data['resources'] = resources
    print("\n< summary: {}".format(data))
    answer = input("> do you confirm the reservation? [Y/n] ")
    if answer.lower() is not 'y' and answer.lower() is not 'yes':
        print('* aborting...')
        sys.exit()
    response = api('sites/{}/jobs'.format(site), r_type='post', headers={'Content-Type': 'application/json'}, data=data)
    if response.status_code == 201:
        print('success!')
        print('URI of the newly created job: {}'.format(response.headers['Location']))
    else:
        print('error: status_code={}'.format(response.status_code))
        if response.text:
            print(response.text)

def get_parameters(site):
    data = {
        'site': site,
        'walltime': '01:00',
        'num_nodes': '1',
        'command': 'sleep 10d'
    }
    clusters = list_site_clusters(site, clusters_list=True)
    print('< available clusters in {}: {}'.format(site, clusters))
    repeat=True
    multiple_clusters=False
    while repeat:
        cluster = input('> cluster name (optional): ')
        if cluster.strip():
            if cluster.lower() in clusters:
                data['cluster'] = cluster.lower()
            else:
                print ('< error: {} not in avaiable clusters ({})'.format(cluster, clusters))
                repeat = True
                continue
        repeat = False
    if not data.get('cluster'):
        num_clusters = input('> number of clusters (optional): ')
        if num_clusters.strip():
            data['num_clusters'] = num_clusters
            multiple_clusters=True
    num_nodes = input('> number of {} (default=1): '.format('nodes per cluster' if multiple_clusters else 'nodes'))
    if num_nodes.strip():
        data['num_nodes'] = num_nodes
    walltime = input('> walltime (hh:mm) (default=1): ')
    if walltime.strip():
        data['walltime'] = walltime
    start_at = input('> start at [GMT+2, FR] (yyyy-dd-mm hh:mm:ss) (default=as soon as possible): ')
    if start_at.strip():
        data['start_at'] = start_at
    command = input('> command/script (default=sleep 10d): ')
    if command.strip():
        data['command'] = command
    return data

def delete_job(site, job_id):
    response = api('sites/{}/jobs/{}'.format(site, job_id), r_type='delete')
    if response.status_code == 202:
        print('success, deletion request has been accepted!')
        print('job URI (use it to poll for the error state): {}'.format(response.headers['Location']))
    else:
        print('error: status_code={}'.format(response.status_code))
        print(response.text)

def main():
    parser = argparse.ArgumentParser(description="A simple Python wrapper for GRID'5000 RESTful API")
    parser.add_argument('--list_sites', action="store_true", help='list all GRID\'5000 sites')
    parser.add_argument('--list_clusters', help='list all clusters in the given site', metavar=('SITE_NAME'))
    parser.add_argument('--list_nodes', nargs=2, help='list all nodes in the given site and cluster', metavar=('SITE_NAME', 'CLUSTER_NAME'))
    parser.add_argument('--site_status', help='print the status of the given site', metavar=('SITE_NAME'))
    parser.add_argument('--verbose', '-v',  action="store_true", help='verbose output')
    parser.add_argument('--grid_status',  action="store_true", help="print GRID'5000 status (available nodes on each site)")
    parser.add_argument('--sub', help="make a reservation in the given site", metavar=('SITE_NAME'))
    parser.add_argument('--cancel', nargs=2, help="cancel a reservation or delete a job", metavar=('SITE_NAME', 'JOB_ID'))

    args = parser.parse_args()
    if len(sys.argv) == 1 or len(sys.argv) == 2 and args.verbose:
        parser.print_usage()
        sys.exit(1)
    if args.sub:
        try:
            make_reservation(site=args.sub)
        except Exception as e:
            print(e)
        finally:
            sys.exit(1)
    if args.cancel:
        delete_job(site=args.cancel[0], job_id=args.cancel[1])
    if args.list_sites:
        list_sites()
    if args.list_clusters:
        list_site_clusters(site=args.list_clusters)
    if args.list_nodes:
        list_cluster_nodes(site=args.list_nodes[0], cluster=args.list_nodes[1])
    if args.site_status:
        check_site_status(site=args.site_status, verbose=args.verbose)
    if args.grid_status:
        check_grid_status()

if __name__ == '__main__':
    main()
