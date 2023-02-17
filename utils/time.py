# Copyright (c) 2022-2023 SpikeBonjour
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime


def to_duration(time: str) -> datetime.timedelta:
    """
    Convert a time string to a ``datetime.timedelta`` object.

    :param time: The time string.
    :return: The duration converted.
    """
    time_data = {"d": 0, "h": 0, "m": 0, "s": 0}

    buffer = ""
    for i in time:
        if i.isnumeric():
            buffer += str(i)
        if i in ("h", "m", "s", "M", "d", "y"):
            time_data[i] = int(buffer)

    dur = datetime.timedelta(
        seconds=time_data["s"],
        minutes=time_data["m"],
        hours=time_data["h"],
        days=time_data["d"],
    )
    return dur
