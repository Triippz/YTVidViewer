import json
from queue import Queue

import requests
from bs4 import BeautifulSoup

from proxy.proxy_queue import ProxyQueue
from util.log import LOG


class IP(object):
    """ Provides a Non-Suspicious IP address """

    def __init__(self, proto, worker_name):
        self.proxy_queue = ProxyQueue()
        self.ip_check = 'https://ip-api.io/json/{}'
        self.proto = proto
        self.ip_info = {}
        self.used_ip_queue = Queue()
        self.worker_name = worker_name
        self.current_ip = ""
        self.current_port = 0

        self.set_ip()

    def set_ip(self):
        """
        Set's the IP address of the object. If the proxy IP is
        found to be suspicious, we remove it from our queue of proxies
        and reload a new one, and check again (recursively). If we somehow
        are reusing a previously used proxy, we will rotate.
        :return: None
        """
        LOG.INFO("Setting new IP for {}".format(self.worker_name))
        self.proxy_queue.load_proxy()
        if not self.examine_ip(self.proxy_queue.get_current_proxy()['ip']):
            LOG.WARN("{} - {}:{} is suspicious, obtaining new...".format(self.worker_name, self.get_ip(), self.get_port()))
            self.proxy_queue.load_new_proxy()
            self.set_ip()
        self.current_ip = str(self.proxy_queue.get_current_proxy()['ip'])
        self.current_port = int(self.proxy_queue.get_current_proxy()['port'])
        LOG.INFO("IP set for {} - {}:{}".format(self.worker_name, self.get_ip(), self.get_port()))

    def examine_ip(self, ip):
        """
        Scrapes a website to validate if an IP is suspicious or not
        :param ip: The ip address to search
        :return: True/False
        """
        page = requests.get(self.ip_check.format(ip))
        soup = BeautifulSoup(page.content, "html.parser")
        self.ip_info = json.loads(soup.contents[0])
        susp_fact = self.ip_info['suspiciousFactors']
        return not all([susp_fact['isProxy'], susp_fact['isSuspicious'], susp_fact['isTorNode'], susp_fact['isSpam']])

    def get_ip(self):
        """
        Gets the current IP address from the proxy being used
        :return: Proxy IP
        """
        return self.current_ip

    def get_port(self):
        """
        Gets the current Port from the proxy being used
        :return: Proxy port
        """
        return self.current_port

    def get_ip_info(self):
        """
        Returns the json response of the Proxy's Information
        :return: Proxy Info
        """
        return self.ip_info

    def rotate_proxy(self):
        """
        Rotates a proxy. Aka, removes the current (active) Proxy IP and
        loads in a new "Clean" one. If proxy already used, we will re-rotate (recursively)
        :return: None
        """
        LOG.INFO("Rotating Proxy for: {}".format(self.worker_name))
        # Add the "old" proxy to our used queue
        self.used_ip_queue.put(self.proxy_queue.get_current_proxy())

        self.proxy_queue.load_new_proxy()
        if self.exists_in_queue():
            self.rotate_proxy()

        if not self.examine_ip(self.proxy_queue.get_current_proxy()['ip']):
            self.proxy_queue.load_new_proxy()
            self.set_ip()

        self.current_ip = str(self.proxy_queue.get_current_proxy()['ip'])
        self.current_port = int(self.proxy_queue.get_current_proxy()['port'])

    def exists_in_queue(self):
        for proxy in iter(self.used_ip_queue.get, None):
            if proxy == self.proxy_queue.get_current_proxy():
                return True
        return False

