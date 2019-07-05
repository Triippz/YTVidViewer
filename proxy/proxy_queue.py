import random

import requests
from bs4 import BeautifulSoup


class ProxyQueue(object):

    def __init__(self):
        """
        Initializes the proxy queue with fresh proxies
        """
        self.proxies = []
        self.current_proxy = {}
        self.proxy_list = 'https://www.sslproxies.org/'

        self.get_proxies()

    def get_proxies(self):
        """
        Scrapes SSLProxies.org for a current list of free proxies,
        which we will use to rotate. Adds then to our queue
        :return:
        """
        page = requests.get('https://www.sslproxies.org/')
        soup = BeautifulSoup(page.content, "html.parser")
        tb = soup.find('table', id='proxylisttable')

        for row in tb.tbody.find_all('tr'):
            self.proxies.append({
                'ip': row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string
            })

    def reload_proxies(self):
        """
        Sets the queue to null and requeries for current proxies
        :return: None
        """
        self.proxies = []
        self.get_proxies()

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
        self.current_proxy = self.proxies[random.randint(0, len(self.proxies) - 1)]

    def load_new_proxy(self):
        """
        Removes the old proxy from the queue and loads a new one
        :return: None
        """
        self.proxies.remove(self.current_proxy)
        self.load_proxy()
