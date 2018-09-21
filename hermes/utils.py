"""
Helper class for regularly used functions
"""
import re

from chatoverflow.chatexchange.events import MessagePosted, MessageEdited
from hermes.logger import main_logger
from hermes import regulars


class utils:
    def __init__(self, room = None, quota = None, config = None, room_owners = None, debug_mode = False):
        if room is not None:
            self.room = room

        if quota is not None:
            self.quota = quota
        else:
            self.quota = -1

        if config is not None:
            self.config = config

        if room_owners is not None:
            self.room_owners = room_owners

        if debug_mode is not None:
            self.debug_mode: debug_mode

    def post_message(self, message, no_main_logger = False, length_check = True):
        """
        Post a chat message
        """
        if not no_main_logger:
            utils.log_message(message)
        self.room.send_message(message, length_check)

    def alias_valid(self, alias):
        """
        Check if the specified alias is valid
        """
        if re.match(r"@[Hh]er[m]?[e]?[s]?", alias) or alias.startswith("@Team/"):
            #Alias valid
            return True
        else:
            #Alias invalid
            return False

    def is_privileged(self, message, include_regulars = False):
        """
        Check if a user is allowed to use privileged commands (usally restricted to bot owners, room owners and moderators)
        """
        priviledged_users = [4733879]
        for owner in self.room_owners:
            priviledged_users.append(owner.id)

        if include_regulars:
            for user in regulars.regulars:
                priviledged_users.append(user)

        # Restrict function to (site) moderators, room owners and maintainers
        if message.user.is_moderator or message.user.id in priviledged_users:
            return True
        else:
            return False

    @staticmethod
    def reply_to(message, reply):
        """
        Reply to the specified message
        """
        utils.log_message(message)
        message.message.reply(reply)

    @staticmethod
    def log_command(command_name):
        """
        Log a command call
        """
        main_logger.info(f"Command call of: {command_name}")

    @staticmethod
    def log_message(message):
        """
        Log a chat message with the message id
        """
        if isinstance(message, MessagePosted) or isinstance(message, MessageEdited):
            main_logger.info(f"Message #{message._message_id} was posted by '{message.user.name}' in room '{message.room.name}'")

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class NoMembersOnlineError(Exception):
    pass

class TeamNotFoundError(Exception):
    pass