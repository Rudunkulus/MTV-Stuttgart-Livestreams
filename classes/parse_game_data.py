import json
import os
import shutil

# paths folders
PATH_FOLDER_IMAGES = "./HTML_Server/images/"
PATH_FOLDER_SERVER = "./HTML_Server/"

# paths files
PATH_JSON = PATH_FOLDER_SERVER + "gamedata.json"
PATH_JSON_TEMP = PATH_FOLDER_SERVER + "gamedata_temp.json"
PATH_FOULS_HOME = PATH_FOLDER_SERVER + "fouls_home.png"
PATH_FOULS_GUEST = PATH_FOLDER_SERVER + "fouls_guest.png"

# substrings
indicator_score = "G305"
indicator_shotclock = "G50"
indicator_teamfouls = "G315"
indicator_gameclock1min = "G36"
indicator_gameclock = "G18"


def parse_data(data_str: str) -> None:
    gamedata = get_old_gamedate()

    if indicator_score in data_str:
        # update score
        score_str = data_str.split(indicator_score)[1][:6]
        scores = parse_score(score_str)
        if scores[0] != "":
            gamedata["score_home"] = scores[0]
        if scores[1] != "":
            gamedata["score_guest"] = scores[1]

    if indicator_shotclock in data_str:
        # update shotclock
        shotclock_str = data_str.split(indicator_shotclock)[1][:7]
        shotclock = parse_shotclock(shotclock_str)
        if shotclock != "":
            gamedata["shotclock"] = shotclock

    if indicator_gameclock in data_str:
        # update gameclock
        gameclock_str = data_str.split(indicator_gameclock)[1][:15]
        [gameclock, quarter] = parse_gameclock(gameclock_str)
        if gameclock != "":
            gamedata["gameclock"] = gameclock
        if quarter != "":
            gamedata["quarter"] = quarter

    if indicator_gameclock1min in data_str:
        # update gameclock1min
        # override other gamclock if possible
        gameclock1min_str = data_str.split(indicator_gameclock1min)[1][:3]
        gameclock = parse_gameclock1min(gameclock1min_str)
        if gameclock != "":
            gamedata["gameclock"] = gameclock

        # if shotclock is more then game time -> disable it
        if gamedata["seconds_shotclock"] > gamedata["seconds_gameclock"]:
            gamedata["shotclock"] = ""

    if indicator_teamfouls in data_str:
        # update teamfouls
        teamfouls_str = data_str.split(indicator_teamfouls)[1][:4]
        teamfouls = parse_teamfouls(teamfouls_str)
        update_teamfouls(teamfouls[0], teamfouls[1])

    write_json(gamedata)


def parse_score(data_str: str) -> tuple[str, str]:
    score_home = ""
    score_guest = ""

    # home score
    if len(data_str) >= 3:
        # can update home score
        if data_str[0].isnumeric():
            # three digits
            if data_str[0:3].isnumeric():
                score_home = data_str[0:3]
        else:
            if data_str[2].isnumeric():
                # two digits
                if data_str[1:3].isnumeric():
                    score_home = data_str[1:3]
            else:
                # one digit
                if data_str[1].isnumeric():
                    score_home = data_str[1]

    # guest score
    if len(data_str) >= 6:
        # can update guest score
        if data_str[5].isnumeric():
            # three digits
            if data_str[3:6].isnumeric():
                score_guest = data_str[3:6]
        else:
            if data_str[3].isnumeric():
                # two digits
                if data_str[3:5].isnumeric():
                    score_guest = data_str[3:5]
            else:
                # one digit
                if data_str[4].isnumeric():
                    score_guest = data_str[4]

    return score_home, score_guest


def parse_teamfouls(data_str: str) -> tuple[str, str]:
    teamfouls_home = ""
    teamfouls_guest = ""

    # home
    if len(data_str) >= 2:
        # can update home team fouls
        if data_str[1].isnumeric():
            teamfouls_home = data_str[1]
    # guest
    if len(data_str) >= 4:
        # can update guest team fouls
        if data_str[3].isnumeric():
            teamfouls_guest = data_str[3]
    return teamfouls_home, teamfouls_guest


def parse_gameclock(data_str: str) -> tuple[str, str]:
    gameclock = ""
    quarter = ""

    if len(data_str) >= 12:
        # can update game time
        # remove first 6 characters
        data_str = data_str[6:]

        if not data_str[5].isnumeric():
            # less than 10 minutes -> add zero as first digit
            data_str = "0" + data_str

        if data_str[0:4].isnumeric():
            minutes = data_str[0:2]
            seconds = data_str[2:4]
            gameclock = minutes + ":" + seconds

        if len(data_str) >= 9:
            # can update quarter
            if data_str[8].isnumeric():
                quarter = "Q" + data_str[8]
    return gameclock, quarter


def parse_gameclock1min(data_str: str) -> str:
    gameclock = ""
    if len(data_str) >= 3:
        # can update game clock
        if data_str[0:3].isnumeric():
            if data_str[0] == "0":
                # less than 10 seconds
                gameclock = data_str[1:2] + "." + data_str[2]
                # hard coding end of quarter
                if gameclock == "0.1":
                    gameclock = "0.0"
            else:
                gameclock = data_str[0:2] + "." + data_str[2]
    return gameclock


def parse_shotclock(data_str: str) -> str:
    shotclock = ""
    if len(data_str) >= 7:
        if data_str[4].isnumeric():
            # two digits
            if data_str[4:6].isnumeric():
                shotclock = data_str[4:6]
        else:
            # single digit
            if data_str[5].isnumeric():
                shotclock = data_str[5]
    return shotclock


def update_teamfouls(fouls_home: str, fouls_guest: str) -> None:
    """Search for the template pictures and overwrite the images which are
    used by the html server

    Parameters:
    fouls_home -- number of home team fouls (integer 0-5)
    guest_home -- number of guest team fouls (integer 0-5)
    """
    # home
    if fouls_home.isnumeric():
        if int(fouls_home) in range(6):
            filename_template = "f_" + fouls_home + ".png"
            shutil.copyfile(
                PATH_FOLDER_IMAGES + filename_template,
                PATH_FOULS_HOME,
            )
        else:
            print(f"Out of Range: cant update home team fouls ({fouls_home})")

    # guest
    if fouls_guest.isnumeric():
        if int(fouls_guest) in range(6):
            filename_template = "f_" + fouls_guest + ".png"
            shutil.copyfile(
                PATH_FOLDER_IMAGES + filename_template,
                PATH_FOULS_GUEST,
            )
        else:
            print(
                "Out of Range: cant update guest team fouls "
                f"({fouls_guest})"
            )


def get_old_gamedate() -> dict:
    try:
        with open(PATH_JSON, "r", encoding="utf-8") as f:
            game_data_old = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        game_data_old = {
            "gameclock": "10:00",
            "quarter": "Q1",
            "shotclock": "24",
            "score_home": "0",
            "score_guest": "0",
        }
    return game_data_old


def init_json() -> None:
    init_data = {
        "gameclock": "10:00",
        "quarter": "-",
        "shotclock": "24",
        "score_home": "0",
        "score_guest": "0",
    }
    update_teamfouls("0", "0")
    write_json(init_data)


def write_json(data: dict) -> None:
    # use temp file to update whole file at once
    with open(PATH_JSON_TEMP, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(PATH_JSON_TEMP, PATH_JSON)
