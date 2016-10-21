#!/usr/bin/env python

from docker import Client

import logging
logger = logging.getLogger('docker_netscaler')

class DockerInterface:

    def __init__(self):
        self.client = Client(base_url='unix://var/run/docker.sock')

    def get_service_members(self, svc_label_key, svc_label_value):
        svc_label = svc_label_key + "=" + svc_label_value
        logger.info("Getting backends for svc label %s" % svc_label)
        containers = self.client.containers(filters={'status': 'running',
                                                     'label': [svc_label]})
        # assuming single network and single port 
        ips = [c['NetworkSettings']['Networks'].values()[0]['IPAddress'] for c in  containers]
        ports = [c['Ports'][0]['PrivatePort'] for c in containers]

        # return list of tuple of ip, port [('172.22.0.2', 80), ('172.22.0.3', 80)]
        return zip(ips, ports)

    def get_service_url(self, svc_label_key, svc_label_value, svc_url_key):
        svc_label = svc_label_key + "=" + svc_label_value
        logger.info("Getting backends for svc label %s" % svc_label)
        containers = self.client.containers(filters={'status': 'running',
                                                     'label': [svc_label]})
        label_values = [c['Labels'][svc_url_key] for c in  containers]

        return label_values[0] # assume that all values in the list are identical

    def get_cpx_port(self):
        cpxs = self.client.containers(filters={'name': 'cpx'})
        port = [port['PublicPort'] for port in cpxs[0]['Ports'] if port['PrivatePort'] == 80]
        return port[0]

