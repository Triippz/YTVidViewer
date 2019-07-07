#      YTVieViewer, YouTube viewer bot for educational purposes
#      Copyright (C) 2019  Mark Tripoli
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

import sys


class LOG(object):
    @staticmethod
    def INFO(message, end="\n"):
        sys.stdout.write('\x1b[1;34m' + "[INFO]- " + message.strip() + '\x1b[0m' + end)
        sys.stdout.flush()

    @staticmethod
    def WARN(message, end="\n"):
        sys.stderr.write('\x1b[1;33m' + "[WARN]- " + message.strip() + '\x1b[0m' + end)
        sys.stdout.flush()

    @staticmethod
    def ERROR(message, end="\n"):
        sys.stderr.write('\x1b[1;31m' + "[ERROR]- " + message + '\x1b[0m' + end)
        sys.stdout.flush()

    @staticmethod
    def FATAL(message, end="\n"):
        sys.stderr.write('\x1b[1;31m' + "[FATAL]- " + message + '\x1b[0m' + end)
        sys.stdout.flush()

    @staticmethod
    def DEBUG(message, end="\n"):
        sys.stdout.write('\033[34m' + "[FATAL]- " + message + '\x1b[0m' + end)
        sys.stdout.flush()

    @staticmethod
    def STATUS(message, end="\n"):
        sys.stdout.write(message + end)
        sys.stdout.flush()
