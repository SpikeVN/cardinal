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

import os

import yaml

import logger

CONFIG_HIVE: dict


def init_config_hive():
    """Initialize the RAM config storage."""
    with open("config.yaml", "r") as f:
        global CONFIG_HIVE
        CONFIG_HIVE = yaml.safe_load(f.read())


def get(_i: str) -> any:
    """
    Get entry from the config file or environment variables.
    For example: ``general.token``

    :param _i: the configuration location identifier.
    :return: its value.
    """
    if _i in os.environ:
        if (
            "password" in _i
            or "token" in _i
            or "key" in _i
            or "email" in _i
            or "url" in _i
        ):
            logger.debug(f"   ---> {len(os.environ[_i])*'*'}")
        else:
            logger.debug(f"   ---> {os.environ[_i]}")
        return os.environ[_i]
    path = _i.split(".")
    a = CONFIG_HIVE["config"].copy()
    for i in path:
        a = a[i]
    logger.debug(f"   ---> {a}")
    return None if a == "None" else a


def read(_i):
    """
    Get entry from the config file or environment variables.
    For example: general.token.
    An alias for ``cfgman.get()``

    :param _i: the configuration location identifier.
    :return: its value.
    """
    return get(_i)
