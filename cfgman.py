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
    logger.debug(f"accessing {_i} config entry.")
    if _i in os.environ:
        if "password" in _i or "token" in _i or "key" in _i or "email" in _i or "url" in _i:
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
