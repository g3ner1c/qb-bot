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
