#!/usr/bin/env python
import logging
from netscaler import NetscalerInterface
from dockr import DockerInterface

logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s  - %(levelname)s - [%(filename)s:%(funcName)-10s]  (%(threadName)s) %(message)s')
logger = logging.getLogger('docker_netscaler')
logger.addFilter(logging.Filter('docker_netscaler'))
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    dockr = DockerInterface()
    nsport = dockr.get_cpx_port()
    netskaler = NetscalerInterface('127.0.0.1', 'nsroot',
                                   'nsroot', str(nsport))
    logger.info("NS_PORT %s" % str(nsport))

    services = ["accounts", "cart", "catalog"]
    services_urls = {}
    for svc in services:
        url = dockr.get_service_url('com.widgetshop.service', svc,
                                    'com.widgetshop.url')
        logger.info("Service: %s, url: %s" % (svc, url))
        services_urls[svc] = url
    netskaler.configure_cs_frontend("WidgetShop", "127.0.0.1",
                                    88, services_urls)

    for svc in services:
        ip_ports = dockr.get_service_members('com.widgetshop.service', svc)
        logger.info("Service: %s, ip_ports=%s", svc, ip_ports)
        for ip_port in ip_ports:
            netskaler.add_service(svc, ip_port[0], ip_port[1])
