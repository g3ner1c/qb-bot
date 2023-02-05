"""Helper functions."""

import aiohttp
from lib.consts import ALIASES, ALL_ALIASES, CATEGORIES, SUBCATEGORIES


def parse_int_range(int_ranges: list[str]) -> list[int]:
    """Parse a list of stringed difficulty ranges into a list of integers.

    Args:
        int_ranges (list[str]): A list of difficulty ranges.

        If there are multiple ranges, the output will be the union of all ranges.

        Ranges can be of the following forms: `n`, `n-`, `n-m`, `n+`, `<n`, `<=n`, `>n`, `>=n`

        Diffculties can be from 0 to 10:

            `0`: Unrated, usually niche packets written for fun (uncommon)
            `1`: Middle school
            `2`: Easy high school
            `3`: Regular high school
            `4`: Hard high school
            `5`: Nationals high school
            `6`: Easy college (1 dot)
            `7`: Regular college (2 dot)
            `8`: Hard college (3 dot)
            `9`: Nationals college (4 dot)
            `10`: Open

    Returns:
        list[int]: A list of integers possible in the given ranges.

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
    """Parse a list of strings of categories and aliases into a list of subcategories.

    Args:
        subcats (list[str]): A list of categories and aliases. (single words)

        Order does matter, this function will try to match the longest possible subcategory out of
        the given words in `subcats`.

        If there are multiple subcategories, the output will be the union of all subcategories.

    Returns:

        list[str]: A list of subcategories.


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
    """Generate paramenters for a request to the random question API.

    Args:
        question_type (str): The type of question to request. Can be "tossup" or "bonus".
        argv (list[str]): A list of arguments to parse, straight from user input.

    Returns:
        dict: A dictionary of parameters to pass to the API.

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


async def check_answer(answerline: str, answer: str, client: aiohttp.ClientSession) -> str:
    """Check if an answer is correct using the QB Reader API.

    Args:
        answerline (str): The answerline of the question.
        answer (str): The answer to check.
        client (aiohttp.ClientSession): `aiohttp` client session.

    Returns:
        str: The result of the check. Can be "accept", "reject", or "prompt"
    """

    async with client.get(
        "https://www.qbreader.org/api/check-answer",
        params={"answerline": answerline, "givenAnswer": answer},
    ) as r:
        return await r.json(content_type="text/html")
