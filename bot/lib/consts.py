"""Constants and aliases."""

import os
from json import load

try:
    from dotenv import load_dotenv

    load_dotenv()

except ImportError:
    if os.path.exists(".env"):
        print(
            ".env file found but dotenv is not installed, please install the dev dependencies with 'poetry install'"  # noqa: E501
        )
        exit(1)


CLIENT_ID = os.getenv("CLIENT_ID")
INVITE = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&scope=bot"

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print(
        "no token found, please add a token to a .env file or set the TOKEN environment variable"
    )
    exit(1)

CONFIG_PATH = "config.json"

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        with open("config_default.json") as default:
            f.write(default.read())

with open(CONFIG_PATH) as f:
    config = load(f)

PREFIX = config["prefix"]
C_NEUTRAL = int(config["embed_colors"]["neutral"], 16)
C_ERROR = int(config["embed_colors"]["error"], 16)
C_SUCCESS = int(config["embed_colors"]["success"], 16)

QBREADER_API = "https://www.qbreader.org/api"

CATEGORIES = [
    "Literature",
    "History",
    "Science",
    "Fine Arts",
    "Religion",
    "Mythology",
    "Philosophy",
    "Social Science",
    "Current Events",
    "Geography",
    "Other Academic",
    "Trash",
]
SUBCATEGORIES = {
    "Literature": [
        "American Literature",
        "British Literature",
        "Classical Literature",
        "European Literature",
        "World Literature",
        "Other Literature",
    ],
    "History": [
        "American History",
        "Ancient History",
        "European History",
        "World History",
        "Other History",
    ],
    "Science": ["Biology", "Chemistry", "Physics", "Math", "Other Science"],
    "Fine Arts": ["Visual Fine Arts", "Auditory Fine Arts", "Other Fine Arts"],
    "Religion": ["Religion"],
    "Mythology": ["Mythology"],
    "Philosophy": ["Philosophy"],
    "Social Science": ["Social Science"],
    "Current Events": ["Current Events"],
    "Geography": ["Geography"],
    "Other Academic": ["Other Academic"],
    "Trash": ["Trash"],
}
ALIASES = {
    "Literature": ["l", "lit"],
    "American Literature": ["am lit", "us lit", "ameri lit", "american lit"],
    "British Literature": ["brit lit", "british lit"],
    "Classical Literature": ["classic", "classics", "classical lit"],
    "European Literature": ["euro lit", "european lit"],
    "World Literature": ["world lit"],
    "Other Literature": ["other lit"],
    "History": ["h", "hist"],
    "American History": ["am hist", "us hist", "ameri hist", "american hist"],
    "Ancient History": ["ancient hist"],
    "European History": ["euro hist", "european hist"],
    "World History": ["world hist"],
    "Other History": ["other hist"],
    "Science": ["sci"],
    "Biology": ["bio"],
    "Chemistry": ["chem"],
    "Physics": ["phys"],
    "Math": ["mathematics", "maths"],
    "Other Science": ["other sci"],  # no cs :(
    "Fine Arts": ["fa", "arts", "fine art"],
    "Visual Fine Arts": ["vfa", "vis fa", "vis arts", "vis fine art"],
    "Auditory Fine Arts": ["afa", "audio fa", "audio arts", "audio fine art"],
    "Other Fine Arts": ["other fa", "other arts", "other fine art"],
    "Religion": ["r", "rel"],
    "Mythology": ["m", "myth"],
    "Philosophy": ["p", "phil"],
    "Social Science": ["ss", "soc sci"],
    "Current Events": ["ce", "curr events"],
    "Geography": ["g", "geo"],
    "Other Academic": ["o", "other academic"],
    "Trash": ["t", "trash"],
}
ALL_ALIASES = sum(ALIASES.values(), [])
