import os
import random
from os import _exit
from platform import system
from subprocess import call
from time import sleep
from traceback import print_exc

from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException
from selenium.webdriver.firefox.options import Options
from proxy.IP import IP
from selenium import webdriver
from os.path import join as path_join
from psutil import Process

from util.log import LOG

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "drivers/")

drivers = []


class ViewerBot(object):

    def __init__(self, worker_name, video_url, cls, driver, watch_length=None):
        super().__init__()
        LOG.INFO("{} initializing . . .".format(worker_name))
        self.bots = 5
        self.worker_name = worker_name
        self.active = False
        self.video_url = video_url
        self.video_name = ""
        self.cls = cls
        self.visits = 0
        self.proto = "https"
        self.ip = IP(self.proto, self.worker_name)
        self.watch_length = watch_length
        self.driver = driver
        self.first_run = True

    def status(self):
        n = '\033[0m'  # null ---> reset
        r = '\033[31m'  # red
        g = '\033[32m'  # green
        y = '\033[33m'  # yellow
        b = '\033[34m'  # blue

        call([self.cls])
        print('')
        print(
            '  +------ {} {} Statistics {} ------+'.format(y, self.worker_name, n))
        print(
            '  [-] Current Video: {}{}{}'.format(g, self.video_url, n))
        print(
            '  [-] Proxy IP: {}{}{}'.format(b, self.ip.proxy_queue.get_current_proxy()['ip'], n))
        print(
            '  [-] Proxies used: {}{}{}'.format(b, self.ip.used_ip_queue.qsize(), n)
        )
        print(
            '  [-] Visits: {}{}{}'.format(y, self.visits, n))

    def useragent(self):
        """
        Selects a random user agent
        :return: user agent
        """
        useragents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) RockMelt/0.9.58.494 Chrome/11.0.696.71 Safari/534.24',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.54 Safari/535.2',
            'Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.348; U; en) Presto/2.5.25 Version/10.54',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.6 (KHTML, like Gecko) Chrome/16.0.897.0 Safari/535.6',
            'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121202 Firefox/17.0 Iceweasel/17.0.1']
        return random.choice(useragents)

    def run(self):
        """

        :return:
        """
        while True:
            try:
                LOG.INFO("{} Starting bot".format(self.worker_name))

                if not self.first_run:
                    self.ip.rotate_proxy()
                else:
                    self.first_run = False

                if self.driver == "chrome":
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('--proxy-server={}'.format(self.ip.get_ip()))
                    chrome_options.add_argument('--user-agent={}'.format(self.useragent()))
                    chrome_options.add_argument('--mute-audio')
                    chrome_options.add_argument('--headless')
                    if system() == 'Windows':
                        executable_path = path_join(DRIVER_BIN, 'chromedriver.exe')
                    elif system() == "Darwin":
                        executable_path = path_join(DRIVER_BIN, 'chromedriver_mac')
                    else:
                        executable_path = path_join(DRIVER_BIN, 'chromedriver_linux')

                    self.driver = webdriver.Chrome(options=chrome_options, executable_path=executable_path)
                else:
                    firefox_profile = webdriver.FirefoxProfile()
                    firefox_profile.set_preference("media.volume_scale", '0.0')
                    firefox_profile.set_preference('general.useragent.override', self.useragent())
                    firefox_profile.set_preference('network.proxy.type', 1)
                    firefox_profile.set_preference('network.proxy.http', self.ip.get_ip())
                    firefox_profile.set_preference('network.proxy.http_port', int(self.ip.get_port()))
                    firefox_profile.set_preference('network.proxy.ssl', self.ip.get_ip())
                    firefox_profile.set_preference('network.proxy.ssl_port', int(self.ip.get_port()))
                    # firefox_options.preferences.update({
                    #     'media.volume_scale': '0.0',
                    #     'general.useragent.override': self.useragent(),
                    #     'network.proxy.type': 1,
                    #     'network.proxy.http': self.ip.get_ip(),
                    #     'network.proxy.http_port': int(self.ip.get_port()),
                    #     'network.proxy.ssl': self.ip.get_ip(),
                    #     'network.proxy.ssl_port': int(self.ip.get_port())
                    # })
                    # firefox_profile.add_argument('--headless')
                    firefox_profile.update_preferences()
                    options = Options()
                    # options.headless = True

                    if system() == 'Windows':
                        executable_path = path_join(DRIVER_BIN, 'geckodriver_win64.exe')
                    elif system() == "Darwin":
                        if "geckodriver" in os.environ["PATH"]:
                            executable_path = "/usr/local/bin/geckodriver"
                        else:
                            Exception("Geckdriver not found in /usr/local/bin/")
                    else:
                        executable_path = path_join(DRIVER_BIN, 'geckodriver_linux64')

                    self.driver = webdriver.Firefox(firefox_profile=firefox_profile,
                                                    options=options,
                                                    executable_path=executable_path)

                    process = self.driver.service.process
                    pid = process.pid
                    cpids = [x.pid for x in Process(pid).children()]
                    pids = [pid] + cpids
                    drivers.extend(pids)

                    self.watch()

            except WebDriverException as e:
                LOG.WARN('{} - [{}] {}'.format(self.worker_name, id, e.__class__.__name__))
            except KeyboardInterrupt:
                self.exit(0)
            except:
                self.exit(1)
            finally:
                LOG.INFO('{} - [{}] Quitting webdriver!'.format(self.worker_name, id))
                try:
                    self.driver
                except NameError:
                    pass
                else:
                    self.driver.quit()
                with locks[2]:
                    try: pids
                    except NameError:
                        pass
                    else:
                        for pid in pids:
                            try: drivers.remove(pid)
                            except:
                                pass

    def watch(self):
        self.driver.set_page_load_timeout(45)
        self.driver.get(self.video_url)
        self.status()
        if self.driver.title.endswith('YouTube'):
            play_button = self.driver.find_element_by_class_name('ytp-play-button')
            if play_button.get_attribute('title') == 'Play (k)':
                play_button.click()
            if play_button.get_attribute('title') == 'Play (k)':
                raise ElementClickInterceptedException

            if self.watch_length is None:
                video_duration = self.driver.find_element_by_class_name('ytp-time-duration').get_attribute('innerHTML')
                sleep(float(sum([int(x) * 60 ** i for i, x in enumerate(video_duration.split(':')[::-1])])))
            else:
                sleep(self.watch_length)

            LOG.INFO("{} finished watching video".format(self.worker_name))
            self.visits = self.visits + 1

    def exit(self, exit_code):
        global drivers, locks
        try:
            with locks[3]:
                try:
                    drivers
                except NameError:
                    pass
                else:
                    for driver in drivers:
                        try:
                            Process(driver).terminate()
                        except:
                            pass
        except:
            pass
        finally:
            if exit_code:
                print_exc()
            LOG.INFO('\rExitting with code %d\n' % exit_code)
            _exit(exit_code)
