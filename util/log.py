import sys


class LOG(object):
    @staticmethod
    def INFO(message, end="\n"):
        sys.stdout.write('\x1b[1;34m' + "[INFO]- " + message.strip() + '\x1b[0m' + end)

    @staticmethod
    def WARN(message, end="\n"):
        sys.stderr.write('\x1b[1;33m' + "[WARN]- " + message.strip() + '\x1b[0m' + end)

    @staticmethod
    def ERROR(message, end="\n"):
        sys.stderr.write('\x1b[1;31m' + "[ERROR]- " + message + '\x1b[0m' + end)

    @staticmethod
    def FATAL(message, end="\n"):
        sys.stderr.write('\x1b[1;31m' + "[FATAL]- " + message + '\x1b[0m' + end)
