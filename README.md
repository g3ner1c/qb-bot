# qb-bot

An open-source quizbowl discord bot.

All data is sourced from [QB Reader](https://www.qbreader.org/) (check out its [repo](https://www.github.com/qbreader/website) as well!) via its [API](https://www.qbreader.org/api-info).

Contributions are welcome! I licensed this under [AGPLv3](./LICENSE) specifically to encourage contributions.

## Running the bot

### Requirements

This bot requires ***Python 3.10 or higher*** and a discord bot token. You can get a token by creating a new application on the [Discord Developer Portal](https://discord.com/developers/applications).

Make sure you have [Poetry](https://python-poetry.org/) installed as well, if not, you can install it with:

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Then, clone the repository and run `poetry install` to install the dependencies:

```sh
git clone
cd qb-bot
poetry install
```

### Configuration

If there is no `config.json` file in the root directory, the bot will create one for you, using the defaults in [`config_default.json`](./config_default.json).

Variables related to the bot application itself should be set as ***environment variables***.

#### `config.json` fields *(optional to edit)*

- `prefix`: The prefix for the bot's commands. Defaults to `>`.
- `embed_colors`: An object containing hex coded colors for the bot to color embeds with. Defaults to:
  - `neutral`: `0xAE4DFF` (purple)
  - `error`: `0xE02B2B` (red)
  - `success`: `0x00FF00` (green)

#### Environment variables

You can set environment variables in a `.env` file in the root directory or in your shell environment.

- `CLIENT_ID`: The client ID of the bot application (you can find this in the Dev Portal as well).
- `TOKEN`: The bot token (please don't share this with anyone or bad things can happen).

### *Actually* running the bot

Now that you have everything set up, you can simply run the bot with:

```sh
poetry run python3 bot/
```

Congratulations! :D

## Features (may or may not exist)

There are a lot of feature ideas in my head for this bot, but I'm not sure how many I'll actually get around to implementing.
The general idea is to eventually make a "universal" quizbowl bot that can be used for a multitude of purposes.
If you have any feature requests, feel free to open an issue or a pull request.

### Implemented

- Random tossups and bonuses by category and difficulty
- Singleplayer TK and PK sessions

### Ideas

- Multiplayer sessions
- TTS tossup reading
- Database queries
- Playing packets
- Downloading packets
- Buzzer and point tracking aiding a human reader
- Game scoring
