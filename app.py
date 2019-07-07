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


def status(worker_name, proxies, visits, pid):
    global video_url
    n = '\033[0m'  # null ---> reset
    r = '\033[31m'  # red
    g = '\033[32m'  # green
    y = '\033[33m'  # yellow
    b = '\033[34m'  # blue

    status_str = '\n'
    status_str += '  +------ {} {} Statistics {} ------+\n'.format(y, worker_name, n)
    status_str += '  [-] Current Video: {}{}{}\n'.format(g, video_url, n)
    status_str += '  [-] Proxy IP: {}{}{}\n'.format(b, proxies.get_current_proxy()['ip'], n)
    status_str += '  [-] Proxies used: {}{}{}\n'.format(b, proxies.used_proxies.qsize(), n)
    status_str += '  [-] Visits: {}{}{}\n'.format(y, visits, n)
    status_str += '  [-] Process ID: {}{}{}\n'.format(g, pid, n)
    LOG.STATUS(status_str)


def exit(exit_code):
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
        LOG.INFO('Exitting with exit code {}'.format(exit_code))
        _exit(exit_code)


if __name__ == '__main__':
    from os import _exit
    from traceback import print_exc

    while True:
        try:
            import re
            import os
            from os import devnull, environ
            from os.path import isfile, join as path_join
            from time import sleep
            from random import choice
            from psutil import Process
            from platform import system
            from argparse import ArgumentParser
            from threading import Thread, Lock, enumerate as list_threads
            from user_agent import generate_user_agent
            from selenium import webdriver
            from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException
            from selenium.webdriver.firefox.options import Options
            from multiprocessing.pool import Pool
            import stat
            import sys
            from pprint import pprint
            from shutil import copyfile

            import requests
            from PyInquirer import prompt
            from bs4 import BeautifulSoup
            from examples import custom_style_2
            from prompt_toolkit.validation import Validator, ValidationError
            from pyfiglet import figlet_format

            from proxy.proxy_queue import Proxies
            from util.drivers import load_mac_driver, validate_path
            from util.log import LOG
            from util.tools import calc_dur_time
            from fake_useragent import UserAgent

            break
        except:
            exit(1)


def bot(worker_name):
    """

    :return:
    """
    global locks, drivers, video_url, cls, driver, watch_length, api_key

    proxies = Proxies(proto="http", worker_name=worker_name, api_key=api_key)
    first_run = True
    visits = 0

    while True:
        try:
            LOG.INFO("{} Starting bot".format(worker_name))

            if not first_run:
                proxies.rotate_proxy()
            else:
                with locks[0]:
                    proxies.generate_proxies()
                first_run = False

            ua = generate_user_agent(os=('win', 'android'))
            if driver == "chrome":
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--proxy-server={}'.format(proxies.get_ip()))
                chrome_options.add_argument('--user-agent={}'.format(ua))
                chrome_options.add_argument('--mute-audio')
                chrome_options.add_argument('--headless')
                if system() == 'Windows':
                    executable_path = path_join(DRIVER_BIN, 'chromedriver.exe')
                elif system() == "Darwin":
                    executable_path = path_join(DRIVER_BIN, 'chromedriver_mac')
                else:
                    executable_path = path_join(DRIVER_BIN, 'chromedriver_linux')

                driver = webdriver.Chrome(options=chrome_options, executable_path=executable_path)

            else:
                firefox_profile = webdriver.FirefoxProfile()
                firefox_profile.set_preference("media.volume_scale", '0.0')
                firefox_profile.set_preference('general.useragent.override', ua)
                firefox_profile.set_preference('network.proxy.type', 1)
                firefox_profile.set_preference('network.proxy.http', proxies.get_ip())
                firefox_profile.set_preference('network.proxy.http_port', int(proxies.get_port()))
                firefox_profile.set_preference('network.proxy.ssl', proxies.get_ip())
                firefox_profile.set_preference('network.proxy.ssl_port', int(proxies.get_port()))
                firefox_profile.update_preferences()

                options = Options()
                options.headless = True

                if system() == 'Windows':
                    executable_path = path_join(DRIVER_BIN, 'geckodriver_win64.exe')
                elif system() == "Darwin":
                    if "geckodriver" in os.environ["PATH"]:
                        executable_path = "/usr/local/bin/geckodriver"
                    else:
                        Exception("Geckdriver not found in /usr/local/bin/")
                else:
                    executable_path = path_join(DRIVER_BIN, 'geckodriver_linux64')

                driver = webdriver.Firefox(firefox_profile=firefox_profile,
                                           options=options,
                                           executable_path=executable_path)
            # snag the PID of the driver
            process = driver.service.process
            pid = process.pid
            child_pids = [x.pid for x in Process(pid).children()]
            pids = [pid] + child_pids

            # Begin watching
            driver.set_page_load_timeout(45)
            driver.get(video_url)

            # Sometimes pop ups appear we should think about handling them
            if driver.title.endswith('YouTube'):
                play_button = driver.find_element_by_class_name('ytp-play-button')
                if play_button.get_attribute('title') == 'Play (k)':
                    play_button.click()
                if play_button.get_attribute('title') == 'Play (k)':
                    raise ElementClickInterceptedException

                if watch_length is None:
                    video_current = driver.find_element_by_class_name('ytp-time-current').get_attribute(
                        'innerHTML')
                    video_duration = driver.find_element_by_class_name('ytp-time-duration').get_attribute(
                        'innerHTML')
                    duration = calc_dur_time(current_pos=video_current, duration=video_duration)
                    status(worker_name, proxies, visits, pid)
                    sleep(duration)
                else:
                    status(worker_name, proxies, visits, pid)
                    sleep(watch_length)

                LOG.INFO("{} finished watching video".format(worker_name))
                visits += 1

        except WebDriverException as e:
            LOG.WARN('[{}] - [{}] {}'.format(worker_name, id, e.__class__.__name__))
        except KeyboardInterrupt:
            exit(0)
        except:
            exit(1)
        finally:
            LOG.WARN('[{}][{}] Quitting webdriver!'.format(worker_name, id))
            try:
                driver
            except NameError:
                pass
            else:
                driver.quit()
            with locks[2]:
                try:
                    pids
                except NameError:
                    pass
                else:
                    for pid in pids:
                        try:
                            drivers.remove(pid)
                        except:
                            pass


class ValidateUrl(Validator):
    def validate(self, document):
        if document.text == "":
            raise ValidationError(
                message='Please enter a URL',
                cursor_position=len(document.text))  # Move cursor to end


class ValidateAPIKey(Validator):
    def validate(self, document):
        if document.text == "":
            raise ValidationError(
                message='Please enter a valid API Key from https://pubproxy.com',
                cursor_position=len(document.text))  # Move cursor to end
        key = document.text
        page = requests.get("http://pubproxy.com/api/proxy?api={}".format(key))
        if "Invalid API" in page.content.decode("utf-8"):
            raise ValidationError(
                message=page.content.decode("utf-8"),
                cursor_position=len(document.text))  # Move cursor to end
        else:
            pass


def questions():
    yt_vid_question = [
        {
            'type': 'input',
            'name': 'video_url',
            'message': 'What\'s the URL of the YouTube video?',
            'validate': ValidateUrl
        },
        {
            'type': 'list',
            'name': 'driver',
            'message': 'What browser driver would you like to use?',
            'choices': ['Firefox', 'Chrome'],
            'filter': lambda val: val.lower(),
            'default': 'firefox'
        },
        {
            'type': 'password',
            'message': 'This program requires proxies obtained from https://pubproxy.com, please enter your API key.',
            'name': 'api_key',
            'validate': ValidateAPIKey
        },
        {
            'type': 'input',
            'name': 'threads',
            'message': 'How many instances would you like to run?',
        },
    ]
    return prompt(yt_vid_question)


if __name__ == '__main__':
    try:
        print(figlet_format('YTVidViewer!', font='doom'))
        answers = questions()
        api_key = answers['api_key']
        video_url = answers['video_url']
        driver = answers['driver']
        threads = 1
        watch_length = None

        PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        DRIVER_BIN = os.path.join(PROJECT_ROOT, "drivers/")

        validate_path(DRIVER_BIN, driver)
        cls = 'cls' if system() == 'Windows' else 'clear'

        locks = [Lock() for _ in range(4)]
        drivers = []
        workers = []

        bot("Worker 1")

    except SystemExit as e:
        exit(int(str(e)))
    except KeyboardInterrupt:
        exit(0)
    except:
        exit(1)
