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

# Yes, I implement my own logger algorithm.
import datetime
import inspect
import logging
import os

import security

LOG = []

__FORMAT = "{color}[{time} {level}] {file}@{line}: "
LOGFILE = os.path.join("logs", datetime.datetime.now().isoformat() + ".txt")
__MIN_LEVEL = 0

COLOR_BLACK = "\N{ESC}[30m"
COLOR_RED = "\N{ESC}[31m"
COLOR_GREEN = "\N{ESC}[32m"
COLOR_YELLOW = "\N{ESC}[33m"
COLOR_BLUE = "\N{ESC}[34m"
COLOR_MAGENTA = "\N{ESC}[35m"
COLOR_CYAN = "\N{ESC}[36m"
COLOR_WHITE = "\N{ESC}[37m"
COLOR_RESET = " \N{ESC}[0m"

DEBUG = 2
SUCCESS = 1
INFO = 0
WARNING = -1
ERROR = -2
FUCKED = -3

N2LV = {
    "2": "DEBUG",
    "1": "SUCCESS",
    "0": "INFO",
    "-1": "WARNING",
    "-2": "ERROR",
    "-3": "FUCKED",
}
LV2CL = {
    "2": COLOR_WHITE,
    "1": COLOR_GREEN,
    "0": COLOR_RESET,
    "-1": COLOR_YELLOW,
    "-2": COLOR_RED,
    "-3": COLOR_MAGENTA,
}


LOGGING_MAP = {
    "debug": (DEBUG, logging.DEBUG),
    "success": (SUCCESS, logging.INFO),
    "info": (INFO, logging.INFO),
    "warning": (WARNING, logging.WARNING),
    "error": (ERROR, logging.ERROR),
    "fucked": (FUCKED, logging.ERROR),
}


def save_log():
    with open(LOGFILE, "w") as f:
        f.write("\n".join(LOG))


def _log(filename: str, line: int, level: int, *message: str):
    ct = datetime.datetime.now()
    time = f"{ct.hour}:{ct.minute}:{ct.second}"
    if level > __MIN_LEVEL:
        return
    print(
        security.safe_format(
            __FORMAT,
            file=os.path.relpath(filename),
            time=time,
            color=LV2CL[str(level)],
            line=line,
            level=N2LV[str(level)],
        ),
        *message,
        sep="",
    )
    LOG.append(
        security.safe_format(
            __FORMAT,
            file=os.path.relpath(filename),
            time=time,
            color="",
            line=line,
            level=N2LV[str(level)],
        )
        + " ".join(str(message))
    )
    save_log()


def _get_info():
    prop = inspect.getframeinfo(inspect.stack()[2][0])
    return prop.filename, prop.lineno


def set_min_level(level: int | str):
    global __MIN_LEVEL
    if isinstance(level, int):
        __MIN_LEVEL = level
    else:
        __MIN_LEVEL = LOGGING_MAP[level][0]
    logging.basicConfig(
        level=LOGGING_MAP[level][1],
        format="[%(asctime)s %(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def debug(*message: any):
    """do stuffs"""
    a = _get_info()
    _log(a[0], a[1], DEBUG, *message)


def info(*message: any):
    """do stuffs"""
    a = _get_info()
    _log(a[0], a[1], INFO, *message)


def success(*message: any):
    """do stuffs"""
    a = _get_info()
    _log(a[0], a[1], SUCCESS, *message)


def warning(*message: any):
    """do stuffs"""
    a = _get_info()
    _log(a[0], a[1], WARNING, *message)


def error(*message: any):
    """do stuffs"""
    a = _get_info()
    _log(a[0], a[1], ERROR, *message)


def fucked(*message: any):
    """do stuffs"""
    a = _get_info()
    _log(a[0], a[1], FUCKED, *message)
