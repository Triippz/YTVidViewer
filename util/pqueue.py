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
from queue import Queue, Full, Empty


class PQueue(Queue):
    """
    A Checkable Queue with FIFO, dynamically resizes
    """
    def __init__(self, maxsize=1000):
        """Queue constructor."""
        Queue.__init__(self, maxsize=maxsize)

    def __contains__(self, item):
        """Check the Queue for the existence of an item."""
        try:
            # pylint: disable=not-context-manager
            with self.mutex:
                return item in self.queue
        except AttributeError:
            return item in self.queue

    def put(self, item, block=False, timeout=1):
        """Add an item to the Queue."""
        try:
            Queue.put(self, item, block=block, timeout=timeout)
        except Full:
            try:
                self.get_nowait()
            except Empty:
                pass
            self.put(item)

    def all(self, item):
        """Get all the items as a list"""
        return list(self.queue)


