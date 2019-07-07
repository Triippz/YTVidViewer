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
import os
import stat
from platform import system
from shutil import copyfile

from util.log import LOG


def load_win_driver(driver_bin, driver):
    pass


def load_mac_driver(driver_bin, driver):
    # copy our driver to /usr/local/bin
    if driver == "chrome":
        LOG.INFO("Copying chromedriver to system PATH")
        copyfile(driver_bin + "chromedriver_mac", "/usr/local/bin/chromedriver")
        os.environ['PATH'] += os.pathsep + r'/usr/local/bin/chromedriver'
        st = os.stat('/usr/local/bin/chromedriver')
        os.chmod('/usr/local/bin/chromedriver', st.st_mode | stat.S_IEXEC)
        LOG.INFO("chromedriver set in PATH (/usr/local/bin/chromedriver)")
    else:
        LOG.INFO("Copying geckodriver to system PATH")
        copyfile(driver_bin + "geckodriver_mac", "/usr/local/bin/geckodriver")
        os.environ['PATH'] += os.pathsep + r'/usr/local/bin/geckodriver'
        st = os.stat('/usr/local/bin/geckodriver')
        os.chmod('/usr/local/bin/geckodriver', st.st_mode | stat.S_IEXEC)
        LOG.INFO("Geckodriver set in PATH (/usr/local/bin/geckodriver)")


def load_linux_driver(driver_bin, driver):
    pass


def validate_path(driver_bin, driver):
    if driver == "chrome":
        pass
    else:
        if system() == 'Windows':
            pass
        elif system() == "Darwin":
            if "geckodriver" not in os.environ['PATH']:
                LOG.WARN("Geckdriver not found in system PATH, setting now . . .")
                load_mac_driver(driver_bin, driver)
            else:
                LOG.INFO("Geckdriver found in PATH")
        else:
            pass
