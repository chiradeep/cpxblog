#!/usr/bin/env python
import logging
from netscaler import NetscalerInterface
from dockr import DockerInterface

logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s  - %(levelname)s - [%(filename)s:%(funcName)-10s]  (%(threadName)s) %(message)s')
logger = logging.getLogger('docker_netscaler')
logger.addFilter(logging.Filter('docker_netscaler'))
logger.setLevel(logging.DEBUG)

SVC_LABEL_NAME = 'com.widgetshop.service'
SVC_LABEL_URL = 'com.widgetshop.url'

CS_VSERVER_NAME = 'WidgetShop'
CS_VSERVER_PORT = 88

CPX_CONTAINER_NAME = 'cpx'

if __name__ == '__main__':
    dockr = DockerInterface()

    # find the exposed Netscaler port
    nsport = dockr.get_ns_port(CPX_CONTAINER_NAME)
    logger.info("NS_PORT %s" % str(nsport))

    # Use default credentials
    netskaler = NetscalerInterface('127.0.0.1', 'nsroot',
                                   'nsroot', str(nsport))

    services = ["accounts", "cart", "catalog"]
    services_urls = {}

    for svc in services:
        url = dockr.get_service_url(SVC_LABEL_NAME, svc, SVC_LABEL_URL)
        logger.info("Service: %s, url: %s" % (svc, url))
        services_urls[svc] = url

    netskaler.wait_for_ready()

    # create cs vserver, lb vservers and service groups
    netskaler.configure_cs_frontend(CS_VSERVER_NAME, "127.0.0.1",
                                    CS_VSERVER_PORT, services_urls)

    # populate service group members into service groups
    for svc in services:
        ip_ports = dockr.get_service_members(SVC_LABEL_NAME, svc)
        logger.info("Service: %s, ip_ports=%s", svc, ip_ports)
        for ip_port in ip_ports:
            netskaler.add_service(svc, ip_port[0], ip_port[1])
