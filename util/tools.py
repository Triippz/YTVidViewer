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


def calc_dur_time(current_pos, duration):
    dur_float = float(sum([int(x) * 60 ** i for i, x in enumerate(duration.split(':')[::-1])]))
    cur_float = float(sum([int(x) * 60 ** i for i, x in enumerate(current_pos.split(':')[::-1])]))
    total_time = dur_float - cur_float
    return total_time
