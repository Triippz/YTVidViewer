#      YTVieViewer, YouTube viewer bot for educational purposes
#      Copyright (C)  2019  Mark Tripoli
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import random
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from util.exceptions import OverstayException
from util.log import LOG
from util.pqueue import PQueue

ip_check_url = 'https://ip-api.io/json/{}'


class Proxies(object):

    def __init__(self, worker_name, api_key, proto, check_suspicious=False):
        """
        Initializes the proxy queue with fresh proxies
        """
        self.proxies = []
        self.used_proxies = PQueue()
        self.worker_name = worker_name
        self.proto = proto
        self.api_key = api_key
        self.current_proxy = {}
        self.current_ip = ""
        self.current_port = 0
        self.proxy_list = 'https://www.sslproxies.org/'
        self.check_suspicious = check_suspicious

    def generate_proxies(self):
        """
        Generates proxies from PubProxy.com, then assigns our first usable
        proxy for use.
        :return: None
        """
        prox_page = requests.get("http://pubproxy.com/api/proxy?api={}&limit=20&https=true&format=json".format(self.api_key)).json()

        for entry in prox_page['data']:
            self.proxies.append({
                'ip': entry['ip'],
                'port': entry['port']
            })
        self.load_proxy()

    def suspicious_proxy(self, ip):
        """
        Scrapes a website to validate if an IP is suspicious or not
        :param ip: The ip address to search
        :return: True/False
        """
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        https_proxy = "https://" + self.current_proxy['ip'] + ":" + self.current_proxy['port']
        proxy_dict = {"https": https_proxy}

        page = requests.get(ip_check_url.format(ip), proxies=proxy_dict)
        soup = BeautifulSoup(page.content, "html.parser")
        try:
            susp_fact = json.loads(soup.contents[0])['suspiciousFactors']
            value = susp_fact['isSpam']
            return not value
        except KeyError:
            raise OverstayException

    def reload_proxies(self):
        """
        Sets the queue to null and requeries for current proxies
        :return: None
        """
        self.proxies = []
        self.generate_proxies()

    def get_current_proxy(self):
        """
        Returns the currently loaded proxy
        :return: current proxy
        """
        return self.current_proxy

    def load_proxy(self):
        """
        Loads a new random proxy
        :return: None
        """
        try:
            self.current_proxy = self.proxies[random.randint(0, len(self.proxies) - 1)]
        except:
            self.generate_proxies()

    def load_new_proxy(self):
        """
        Removes the old proxy from the queue and loads a new one
        :return: None
        """
        self.proxies.remove(self.current_proxy)
        self.load_proxy()

    def new_proxy(self):
        """
        Removes the old proxy adds the new, updates all info.
        Performs a check to ensure the new proxy has not been used
        :return: None
        """
        self.load_new_proxy()
        while self.is_used():
            self.load_new_proxy()

        self.current_port = int(self.current_proxy['port'])
        self.current_ip = str(self.current_proxy['ip'])

    def rotate_proxy(self):
        """
        Rotates a proxy. Aka, removes the current (active) Proxy IP and
        loads in a new "Clean" one. If proxy already used, we will re-rotate (recursively)
        :return: None
        """
        LOG.WARN("Rotating Proxy for: {}".format(self.worker_name))

        # Put the current proxy in the used Queue
        self.used_proxies.put(self.get_current_proxy())

        # Set a new proxy as the current
        self.new_proxy()

    def is_used(self):
        exists = self.used_proxies.__contains__(self.get_current_proxy())
        if exists:
            LOG.DEBUG("{}:{} exists in queue".format(self.get_current_proxy()['ip'],
                                                     self.get_current_proxy()['port']))
        return exists

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

