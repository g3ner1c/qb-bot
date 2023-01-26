"""Constants and aliases."""

from json import load

with open("config.json") as file:
    config = load(file)

PREFIX = config["prefix"]
INVITE = config["invite"]
C_NEUTRAL = int(config["embed_colors"]["neutral"], 16)
C_ERROR = int(config["embed_colors"]["error"], 16)
C_SUCCESS = int(config["embed_colors"]["success"], 16)

API_RANDOM_QUESTION = "https://www.qbreader.org/api/random-question"

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
    "Math": ["math"],
    "Other Science": ["other sci"],
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
