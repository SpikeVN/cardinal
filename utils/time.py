#  Copyright (c) 2022-2023 The Block Art Online Project contributors.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
