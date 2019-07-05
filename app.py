import os
import stat
import sys
from platform import system
from os.path import join as path_join
from shutil import copyfile
from util.log import LOG

from ViewerBot import ViewerBot

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "drivers/")


def load_win_driver():
    pass


def load_mac_driver(driver):
    # copy our driver to /usr/local/bin
    if driver == "chrome":
        LOG.INFO("Copying chromedriver to system PATH")
        copyfile(DRIVER_BIN + "chromedriver_mac", "/usr/local/bin/chromedriver")
        os.environ['PATH'] += os.pathsep + r'/usr/local/bin/chromedriver'
        st = os.stat('/usr/local/bin/chromedriver')
        os.chmod('/usr/local/bin/chromedriver', st.st_mode | stat.S_IEXEC)
        LOG.INFO("chromedriver set in PATH (/usr/local/bin/chromedriver)")
    else:
        LOG.INFO("Copying geckodriver to system PATH")
        copyfile(DRIVER_BIN + "geckodriver_mac", "/usr/local/bin/geckodriver")
        os.environ['PATH'] += os.pathsep + r'/usr/local/bin/geckodriver'
        st = os.stat('/usr/local/bin/geckodriver')
        os.chmod('/usr/local/bin/geckodriver', st.st_mode | stat.S_IEXEC)
        LOG.INFO("Geckodriver set in PATH (/usr/local/bin/geckodriver)")



def load_linux_driver():
    pass


def validate_path(driver):

    if driver == "chrome":
        pass
    else:
        if system() == 'Windows':
            pass
        elif system() == "Darwin":
            if "geckodriver" not in os.environ['PATH']:
                LOG.WARN("Geckdriver not found in system PATH, setting now . . .")
                load_mac_driver(driver)
            else:
                LOG.INFO("Geckdriver found in PATH")
        else:
            pass


if __name__ == '__main__':
    validate_path("firefox")
    cls = 'cls' if system() == 'Windows' else 'clear'

    bot = ViewerBot(worker_name="Worker 1",
                    video_url="https://www.youtube.com/watch?v=KmFZ2j6IX8U&t=97s",
                    cls=cls,
                    driver="firefox")
    bot.run()
