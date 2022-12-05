from json import load

with open("config.json") as file:
    config = load(file)

PREFIX = config["prefix"]
INVITE = config["invite"]
C_NEUTRAL = int(config["embed_colors"]["neutral"], 16)
C_ERROR = int(config["embed_colors"]["error"], 16)
C_SUCCESS = int(config["embed_colors"]["success"], 16)
