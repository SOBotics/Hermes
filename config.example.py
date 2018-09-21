debug_config = {
    "botParent": "<YOUR_NAME>", # The person which is responsible for running the instance (at best your SE/SO username, so people know whom to ping)
    "botMachine": "<YOUR_MACHINE_NAME>", # The system the bot runs on (example: UbuntuServer).
    "botVersion": "v0.6", # The current version of the Bot, be sure to read the wiki on how to increment the version
    "room": 1, # The ID for the chatroom we work with
    "chatHost": "stackoverflow.com", # The site where the bot runs. Please note that the bot has only been used on stackoverflow.com, and may need changes to work on stackexchange.com
    "email": "", # The credentials to log in a user which posts the messages
    "password": "",
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((", # We shouldn't run out of quota, as they key uses are IP based.
    "redundaKey": "" # Not needed. Feel free to leave this empty
}

prod_config = {
    "botParent": "<YOUR_NAME>",
    "botMachine": "<YOUR_MACHINE_NAME>",
    "botVersion": "v0.6",
    "room": 1,
    "chatHost": "stackoverflow.com",
    "email": "",
    "password": "",
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((",
    "redundaKey": ""
}