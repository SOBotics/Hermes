import os
import sys
import threading
import traceback

from soundflow.logger import main_logger
from soundflow.utils import utils
from chatoverflow.chatexchange.client import Client
from chatoverflow.chatexchange.events import MessagePosted, MessageEdited

import soundflow.redunda as redunda
import soundflow.ping_team as ping_team

#Import config file with custom error message
try:
    import config as config
except ModuleNotFoundError:
    raise Exception("The config module couldn't be imported. Have you renamed config.example.py to config.py?")

utils = utils()

def main():
    """
    Main thread of the bot
    """

    #Get config for the mode (debug/prod)
    try:
        if sys.argv[1] == "--debug":
            print("Loading debug config...")
            utils.config = config.debug_config
            utils.debug_mode = True
        else:
            raise IndexError
    except IndexError:
        print("Loading productive config... \nIf you wanted to load the debug config, use the '--debug' command line option")
        utils.config = config.prod_config

    try:
        #Login and connection to chat
        print("Logging in and joining chat room...")
        client = Client(utils.config["chatHost"])
        client.login(utils.config["email"], utils.config["password"])
        room = client.get_room(utils.config["room"])
        room.join()
        room.watch_socket(on_message)
        utils.room = room
        print(room.get_current_user_names())
        utils.room_owners = room.owners

        main_logger.info(f"Joined room '{room.name}' on {utils.config['chatHost']}")

        #Redunda pining
        stop_redunda = threading.Event()
        redunda_thread = redunda.RedundaThread(stop_redunda, utils.config, main_logger)
        redunda_thread.start()

        if utils.debug_mode:
            room.send_message(f"[ [Hermes](https://git.io/fNmlf) ] {utils.config['botVersion']} started in debug mode on {utils.config['botParent']}/{utils.config['botMachine']}.")
        else:
            room.send_message(f"[ [Hermes](https://git.io/fNmlf) ] {utils.config['botVersion']} started on {utils.config['botParent']}/{utils.config['botMachine']}.")


        while True:
            message = input()

            if message in ["restart", "reboot"]:
                os._exit(1)
            else:
                room.send_message(message)

    except KeyboardInterrupt:
        os._exit(0)
    except BaseException as e:
        print(e)
        os._exit(1)

def on_message(message, client):
    """
    Handling the event if a message was posted, edited or deleted
    """
    if not isinstance(message, MessagePosted) and not isinstance(message, MessageEdited):
        # We ignore events that aren't MessagePosted or MessageEdited events.
        return

    #Check that the message object is defined
    if message is None or message.content is None:
        main_logger.warning("ChatExchange message object or content property is None.")
        main_logger.warning(message)
        return

    #Get message as full string and as single words
    message_val = message.content
    words = message.content.split()

    #Check for non-alias-command calls
    if message.content.startswith("🚂"):
        utils.log_command("train")
        utils.post_message("🚃")
    elif message.content.lower().startswith("@bots alive"):
        utils.log_command("@bots alive")
        utils.post_message("All circuits operational.")

    #Check if alias is valid
    if not utils.alias_valid(words[0]):
        return

    #Check if command is not set
    if len(words) <= 1 and message_val.startswith("@Team/"):
        utils.reply_to(message, "You may want to pass a message.")
        return
    elif len(words) <= 1:
        utils.reply_to(message, "You may want to pass a command.")
        return

    #Store command in it's own variable
    command = words[1]
    full_command = ' '.join(words[1:])

    #Here are the commands defined
    try:
        if command in ["del", "delete", "poof"]:
            msg = client.get_message(message.parent_message_id)
            if msg is not None:
                if utils.is_privileged(message):
                    msg.delete()
                else:
                    utils.reply_to(message, "This command is restricted to moderators, room owners and maintainers.")
        if words[0].startswith("@Team/"):
            if utils.is_privileged(message, True):
                utils.log_command("team ping")

                if full_command is "@Team/":
                    utils.reply_to(message, "Please specify a team.")
                    return

                team_name = words[0].replace("@Team/", "")

                if words[1] in ["--members", "--whois"]:
                    ping_team.get_members(team_name, utils)
                elif words[1] in ["--here", "--online"]:
                    ping_team.get_online_members(team_name, utils)
                else:
                    ping_team.ping_team(team_name, full_command, utils)
            else:
                utils.reply_to(message, "Sorry, but only moderators, room owners and approved regulars are allowed to use this command")

        if command in ["amiprivileged"]:
            utils.log_command("amiprivileged")

            if utils.is_privileged(message, True):
                utils.reply_to(message, "You are privileged.")
            else:
                utils.reply_to(message, "You are not privileged. Ping @Team/HermesDevs if you believe that's an error.")
        elif command in ["a", "alive"]:
            utils.log_command("alive")
            utils.reply_to(message, "All circuits operational.")
        elif command in ["v", "version"]:
            utils.log_command("version")
            utils.reply_to(message, f"Current version is {utils.config['botVersion']}")
        elif command in ["loc", "location"]:
            utils.log_command("location")
            utils.reply_to(message, f"This instance is running on {utils.config['botParent']}/{utils.config['botMachine']}")
        elif command in ["kill", "stop"]:
            utils.log_command("kill")
            main_logger.warning(f"Termination or stop requested by {message.user.name}")

            if utils.is_privileged(message):
                try:
                    utils.room.leave()
                except BaseException:
                    pass
                raise os._exit(0)
            else:
                utils.reply_to(message, "This command is restricted to moderators, room owners and maintainers.")
        elif command in ["update"]:
            utils.log_command("update")

            # Restrict function to maintainers
            if message.user.id == 4733879:
                utils.post_message("Pulling from GitHub...")
                os.system("git config core.fileMode false")
                os.system("git reset --hard origin/master")
                os.system("git pull")
                raise os._exit(1)
            else:
                utils.reply_to(message, "This command is restricted to bot maintainers.")
        elif command in ["reboot"]:
            utils.log_command("reboot")
            main_logger.warning(f"Restart requested by {message.user.name}")

            if utils.is_privileged(message):
                try:
                    utils.post_message("Rebooting now...")
                    utils.room.leave()
                except BaseException:
                    pass
                raise os._exit(1)
            else:
                utils.reply_to(message, "This command is restricted to moderators, room owners and maintainers.")
        elif command in ["commands", "help"]:
            utils.log_command("command list")
            utils.post_message("    ### SoundFlow commands ###\n" + \
                               "    amiprivileged                 - Checks if you're allowed to run privileged commands\n" + \
                               "    a[live]                       - Replies with a message if the bot is running.\n" + \
                               "    v[ersion]                     - Returns current version\n" + \
                               "    loc[ation]                    - Returns the location of the bot\n" + \
                               "    del[ete], poof                - Deletes a message. Requires privileges.\n" + \
                               "    update                        - Pulls the latest commit from git. Requires maintainer privileges.\n" + \
                               "    reboot                        - Reboots a running instance. Requires privileges.\n" + \
                               "    kill, stop                    - Terminates the bot instance. Requires privileges.\n" + \
                               "    listteams, list teams         - Lists the pingeable teams\n" + \
                               "    @Team/<team name>             - Ping the members of the specified team. Please note that pinging the team can take some time, depending on it's size.\n" + \
                               "    @Team/<team name> --members   - List the members of a team\n" + \
                               "    @Team/<team name> --whois     - List the members of a team\n" + \
                               "    @Team/<team name> --here      - List the members of a team that are currently in the room\n" + \
                               "    @Team/<team name> --online    - List the members of a team that are currently in the room\n", False, False)
        elif full_command in ["listteams", "list teams"]:
            utils.log_command("team list")
            utils.post_message("    I currently know of the following teams:\n" + \
                               "    HermesDevs                 - The developers of Hermes, CheckYerFlags and RankOverflow\n" + \
                               "    HeatDetectorDevs, HDDevs   - The developers of Heat Detector\n" + \
                               "    ThunderDevs                - The developers of Thunder\n" + \
                               "    FireAlarmDevs              - The developers of FireAlarm\n" + \
                               "    RoomOwners                 - The room owners of SOBotics\n" + \
                               "    Admins                     - The admins of SOBotics, which have admin rights on GitHub etc.\n", False, False)
        elif full_command.lower() in ["code", "github", "source"]:
            utils.log_command("code")
            utils.reply_to(message, "My code is on GitHub [here](https://git.io/fNmlf).")
    except BaseException as e:
        main_logger.error(f"CRITICAL ERROR: {e}")
        if message is not None and message.id is not None:
            main_logger.error(f"Caused by message id {message.id}")
            main_logger.error(traceback.format_exc())
        try:
            utils.post_message(f"Error on processing the last command ({e}); rebooting instance... (cc @Filnor)")
            os._exit(1)

        except AttributeError:
            os._exit(1)
            pass


if __name__ == '__main__':
    main()
