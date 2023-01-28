"""Helper functions."""

import aiohttp
from lib.consts import ALIASES, ALL_ALIASES, CATEGORIES, SUBCATEGORIES


def parse_int_range(int_ranges: list[str]) -> list[int]:
    """
    Parse a list of strings into a list of integers.

    Possible values 0-10

    Examples:
    ```
    ['2-', '4-5', '8+'] -> [0, 1, 2, 4, 5, 8, 9, 10]
    ['<3', '>5'] -> [0, 1, 2, 6, 7, 8, 9, 10]
    ['<=3', '>=5'] -> [0, 1, 2, 3, 5, 6, 7, 8, 9, 10]
    ```
    """

    def parse(s: str) -> list[int]:

        if s.startswith("<"):
            if s.startswith("<="):
                return list(range(int(s[2:]) + 1))
            else:
                return list(range(int(s[1:])))

        elif s.startswith(">"):
            if s.startswith(">="):
                return list(range(int(s[2:]), 11))
            else:
                return list(range(int(s[1:]) + 1, 11))

        elif "-" in s:
            start, end = s.split("-")
            if end:
                return list(range(int(start), int(end) + 1))
            else:
                return list(range(int(start)))

        elif "+" in s:
            return list(range(int(s[:-1]), 11))
        else:
            return [int(s)]

    return sorted(set(sum(map(parse, int_ranges), [])))  # flatten and remove duplicates


def parse_subcats(subcats: list[str]) -> list[str]:
    """
    Parse a list of strings of categories and aliases into a list of subcategories.

    Examples:

    ```
    ["math"] -> ["Math"]
    ["lit"] -> ["American Literature", "British Literature", ...]
    ["sci", "us", "hist"] -> ["American History", "Biology", "Chemistry", ...]
    ```
    """

    for index, cat in enumerate(subcats):
        try:
            while (
                expanded_cat := " ".join([cat] + subcats[index + 1 : index + 2])  # noqa: E203
            ) in ALL_ALIASES:
                cat = expanded_cat
                subcats.pop(index + 1)
        except IndexError:
            pass
        subcats[index] = cat

    def parse(s: str) -> list[str]:
        for cat, aliases in ALIASES.items():
            if s == cat.lower() or s in aliases:
                if cat in CATEGORIES:
                    return SUBCATEGORIES[cat]
                else:
                    return [cat]
        return [s]

    return sorted(set(sum(map(parse, subcats), [])))


def generate_params(question_type: str, argv: list[str]) -> dict:
    """
    Generate paramenters for a request to the random question API.
    """

    params = {"questionType": question_type}

    diffs = []
    cats = []

    for arg in argv:

        if any(char.isdecimal() for char in arg):
            diffs.append(arg)

        elif arg.isalpha():
            cats.append(arg)

        else:
            raise ValueError("Invalid argument")

    if diffs:
        params["difficulties"] = parse_int_range(diffs)

    if cats:
        params["subcategories"] = parse_subcats(cats)

    return params


def tossup_read(text: str, chunk_size: int, watch_for_power: bool = True) -> list[str]:
    """
    Parse a tossup into a list of strings where the tossup is gradually revealed.
    `watch_for_power` reads carefully around the power marker if it exists.

    Examples:

    ```
    tossup_read("In quantum mechanics, the square of this quantity is equal to h-bar...", 4) ->
    [
        "In quantum mechanics, the",
        "In quantum mechanics, the square of this quantity",
        "In quantum mechanics, the square of this quantity is equal to h-bar",
        "In quantum mechanics, the square of this quantity is equal to h-bar...",
        ...
    ]
    ```
    """

    text = text.strip().replace("\n", " ").split(" ")
    chunks = []
    seen_power = False

    for i in range(0, len(text), chunk_size):

        next_read = text[: i + chunk_size]

        if watch_for_power and not seen_power and "(*)" in next_read:

            if not next_read[-1].endswith("(*)"):

                power_chunk = next_read[: next_read.index("(*)") + 1]
                chunks.append(" ".join(power_chunk))

            seen_power = True

        chunks.append(" ".join(next_read))

    return chunks


async def check_answer(answerline: str, answer: str, client: aiohttp.ClientSession) -> str:
    """
    Check if an answer is correct using the QB Reader API.

    Returns "accept", "reject", and "prompt"
    """

    async with client.get(
        "https://www.qbreader.org/api/check-answer",
        params={"answerline": answerline, "givenAnswer": answer},
    ) as r:
        return await r.json(content_type="text/html")
