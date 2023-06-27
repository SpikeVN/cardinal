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
import enum

import disnake
import pyrebase

import cfgman
import i18n
import logger

CONFIG = {
    "databaseURL": cfgman.get("backend.firebase.dbURL"),
    "apiKey": cfgman.get("backend.firebase.apiKey"),
    "authDomain": "",
    "storageBucket": "",
    "serviceAccount": "",
}

DATABASE: pyrebase.pyrebase.Database = pyrebase.initialize_app(CONFIG).database()


def initialize_userdata(user: disnake.User):
    """
    Initializes user data with default value.
    """
    DATABASE.child("users").child(user.id).set(
        {
            "punishments": {"banned": False, "kicked": 0, "warned": 0, "isolated": 0},
            "locale": "vi",
            "dm": True,
        }
    )


class UserPunishments(dict):
    def __init__(self, user: disnake.User):
        self.user: disnake.User = user
        self.punishments = (
            DATABASE.child("users").child(self.user.id).child("punishments").get().val()
        )
        super().__init__(**self.punishments)
        self.banned: bool = self.punishments["banned"]
        self.kicked: bool = self.punishments["kicked"]
        self.warned: bool = self.punishments["warned"]
        self.isolated: bool = self.punishments["isolated"]
        if tuple(self.punishments.keys()) != ("banned", "isolated", "kicked", "warned"):
            logger.error(
                f"Faulty user data in database when reading punishments. Resetting users' punishments..."
            )
            DATABASE.child("users").child(user.id).child("punishments").set(
                {"banned": False, "kicked": 0, "warned": 0, "isolated": 0}
            )

    @property
    def banned(self):
        return self.punishments["banned"]

    @property
    def kicked(self):
        return self.punishments["kicked"]

    @property
    def isolated(self):
        return self.punishments["isolated"]

    @property
    def warned(self):
        return self.punishments["warned"]

    @banned.setter
    def banned(self, value: bool):
        DATABASE.child("users").child(self.user.id).child("punishments").child(
            "banned"
        ).set(value)
        self.punishments["banned"] = value

    @kicked.setter
    def kicked(self, value: int):
        DATABASE.child("users").child(self.user.id).child("punishments").child(
            "kicked"
        ).set(value)
        self.punishments["kicked"] = value

    @isolated.setter
    def isolated(self, value: int):
        DATABASE.child("users").child(self.user.id).child("punishments").child(
            "isolated"
        ).set(value)
        self.punishments["isolated"] = value

    @warned.setter
    def warned(self, value: int):
        DATABASE.child("users").child(self.user.id).child("punishments").child(
            "warned"
        ).set(value)
        self.punishments["warned"] = value


class User:
    def __init__(self, base_user: disnake.Member | disnake.User):
        self.user: disnake.User = base_user
        if DATABASE.child("users").child(base_user.id).get().val() is None:
            initialize_userdata(self.user)

    @property
    def punishments(self) -> UserPunishments:
        return UserPunishments(self.user)

    @property
    def locale(self) -> i18n.Locale:
        try:
            return i18n.from_identifier(
                DATABASE.child("users").child(self.user.id).child("locale").get().val()
            )
        except KeyError:
            logger.error(
                f"Faulty user data in database when reading locale. Resetting user's locale..."
            )
            DATABASE.child("users").child(self.user.id).child("locale").set(
                cfgman.get("general.locale")
            )

    @locale.setter
    def locale(self, value: i18n.Locale | disnake.Locale | str):
        DATABASE.child("users").child(self.user.id).child("locale").set(
            value.value.identifier
            if isinstance(value, i18n.Locale)
            else value.value.replace("-", "_")
            if isinstance(value, enum.Enum)
            else value
        )

    @property
    def accept_direct_message(self) -> bool:
        try:
            return DATABASE.child("users").child(self.user.id).child("dm").get().val()
        except KeyError:
            logger.error(
                f"Faulty user data in database when reading DM preference. Resetting user's DM preference..."
            )
            DATABASE.child("users").child(self.user.id).child("dm").set(False)

    @accept_direct_message.setter
    def accept_direct_message(self, value: bool):
        DATABASE.child("users").child(self.user.id).child("dm").set(value)

    def enable_direct_message(self, value: bool):
        DATABASE.child("users").child(self.user.id).child("dm").set(True)

    def disable_direct_message(self, value: bool):
        DATABASE.child("users").child(self.user.id).child("dm").set(False)
