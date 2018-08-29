import soundflow.teams as team_list
from soundflow.utils import Struct


def ping_team(team_name, message, client):
    team = _find_team(team_name)
    if team is not None:
        message = f"{_get_pings(team, client)} {message}"
        return message



def _find_team(team_name):
    for team_raw in team_list.teams:
        team = Struct(**team_raw)
        for alias in team.aliases:
            if alias == team_name:
                return team

def _get_pings(team, client):
    ping_list = ""

    for username in team.members:
        if ping_list == "":
            ping_list = f"@{username}"
            continue
        ping_list = f"{ping_list}, @{username}"

    return ping_list
