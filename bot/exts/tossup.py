"""Tossup commands."""

import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context
from lib.consts import C_ERROR, C_NEUTRAL, C_SUCCESS, QBREADER_API
from lib.utils import check_answer, generate_params
from markdownify import markdownify as md

lock = asyncio.Lock()


class Tossup(commands.Cog, name="tossup commands"):
    """Command class for tossup commands."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def generate_lines(self, text: str, chunk_size: int, watch_power: bool = True) -> list[str]:
        """Parse a tossup into a list of strings where the tossup is gradually revealed.

        Parameters
        ----------
            text : `str`
                The text to parse.
            chunk_size : `int`
                The number of words to include in each chunk.
            watch_power : `bool`, default = `True`
                Read carefully around the power mark.

        Returns
        -------
            `list[str]`
                A list of strings where each string gradually reveals more of the tossup.

        Examples
        --------
        >>> self.generate_lines("In quantum mechanics, the square of this quantity...", 4)
        [
            "In quantum mechanics, the",
            "In quantum mechanics, the square of this quantity",
            "In quantum mechanics, the square of this quantity is equal to h-bar",
            "In quantum mechanics, the square of this quantity is equal to h-bar...",
            ...
        ]
        """
        words = text.strip().replace("\n", " ").split(" ")
        chunks = []
        seen_power = False

        for i in range(0, len(words), chunk_size):
            next_read = words[: i + chunk_size]

            if watch_power and not seen_power and "(*)" in next_read:
                if not next_read[-1].endswith("(*)"):
                    power_chunk = next_read[: next_read.index("(*)") + 1]
                    chunks.append(" ".join(power_chunk))

                seen_power = True

            chunks.append(" ".join(next_read))

        return chunks

    async def play_tossup(self, ctx: Context, params: dict) -> tuple[str, str]:
        """Play a tossup question.

        Parameters
        ----------
            ctx : `discord.ext.commands.Context`
                Message context.
            params : `dict`
                Parameters for the API request.

        Returns
        -------
            answer : `str`
                The formatted answer to the tossup.
            result : `str`
                The result of the tossup.

                Results can be one of the following:

                    `"ended by user"`: user ended the game
                    `"power"`: user answered correctly before the power mark
                    `"correct"`: user answered correctly after the power mark
                    `"neg"`: user answered incorrectly before the tossup is finished reading
                    `"dead"`: user answered incorrectly after the tossup is finished reading
        """
        async with self.bot.session.get(f"{QBREADER_API}/random-tossup", params=params) as r:
            tossup = (await r.json())["tossups"][0]

        tossup_parts = self.generate_lines(tossup["question"], 5)

        footer = [
            tossup["setName"],
            f"Packet {tossup['packetNumber']}",
            f"Tossup {tossup['questionNumber']}",
            f"Difficulty {tossup['difficulty']}",
        ]

        footer = " | ".join(footer)

        can_power = asyncio.Event()
        if "*" in tossup["question"]:
            can_power.set()

        tu_finished = asyncio.Event()

        embed = discord.Embed(title="Tossup", description="", color=C_NEUTRAL)

        embed.set_footer(text=footer)
        tu = await ctx.send(embed=embed)

        try:
            a = tossup["formatted_answer"]
        except KeyError:
            a = tossup["answer"]

        async def edit_tossup():  # reader task
            for part in tossup_parts:
                await asyncio.sleep(0.8)

                async with lock:
                    embed = discord.Embed(title="Tossup", description=part, color=C_NEUTRAL)
                    embed = embed.set_footer(text=footer)
                    await tu.edit(embed=embed)
                    if can_power.is_set() and "*" in part and not part.endswith("(*)"):
                        # include powers right on power mark
                        can_power.clear()

            tu_finished.set()

            await asyncio.sleep(5)

            return "dead"

        reader = asyncio.create_task(edit_tossup())

        async def listen_for_answer(timeout: float | None = None):  # buzzer task
            result = ""

            try:
                buzz = await self.bot.wait_for(
                    "message",
                    check=lambda message: message.author == ctx.author
                    and message.channel == ctx.channel,
                    timeout=timeout,
                )

            except asyncio.TimeoutError:
                reader.cancel()
                await tu.edit(
                    embed=discord.Embed(
                        title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                    ).set_footer(text=footer)
                )
                return "dead"

            if buzz.content.startswith(f"{ctx.prefix}end"):
                reader.cancel()
                await tu.edit(
                    embed=discord.Embed(
                        title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                    ).set_footer(text=footer)
                )
                return "ended by user"

            async with lock:
                await ctx.send(
                    embed=discord.Embed(
                        title="Buzz",
                        description=f"from {ctx.author.mention}",
                        color=C_SUCCESS,
                    )
                )

                if tu_finished.is_set():
                    reader.cancel()

                try:
                    answer = (
                        await self.bot.wait_for(
                            "message",
                            check=lambda message: message.author == ctx.author
                            and message.channel == ctx.channel,
                            timeout=8,  # 8 seconds is the time on protobowl
                        )
                    ).content

                except asyncio.TimeoutError:  # no answer on buzz
                    reader.cancel()
                    await tu.edit(
                        embed=discord.Embed(
                            title="Tossup",
                            description=tossup_parts[-1],
                            color=C_NEUTRAL,
                        ).set_footer(text=footer)
                    )
                    if tu_finished.is_set():
                        return "dead"
                    return "neg"

                while True:
                    if answer.startswith(f"{ctx.prefix}end"):
                        reader.cancel()
                        await tu.edit(
                            embed=discord.Embed(
                                title="Tossup",
                                description=tossup_parts[-1],
                                color=C_NEUTRAL,
                            ).set_footer(text=footer)
                        )
                        return "ended by user"

                    match await check_answer(a, answer, self.bot.session):
                        case ("accept", _):
                            if can_power.is_set():
                                result = "power"
                            else:
                                result = "correct"
                            break

                        case ("reject", _):
                            if tu_finished.is_set():
                                result = "dead"
                            else:
                                result = "neg"
                            break

                        case ("prompt", response):
                            await ctx.send(
                                embed=discord.Embed(
                                    title="prompt",
                                    description=md(response) if response else response,
                                    color=C_NEUTRAL,
                                )
                            )

                            try:
                                answer = (
                                    await self.bot.wait_for(
                                        "message",
                                        check=lambda message: message.author == ctx.author
                                        and message.channel == ctx.channel,
                                        timeout=8,
                                    )
                                ).content

                            except asyncio.TimeoutError:
                                if tu_finished.is_set():
                                    result = "dead"
                                else:
                                    result = "neg"
                                break

                        case _:
                            await ctx.send(
                                embed=discord.Embed(
                                    title="Error",
                                    description="Something went wrong",
                                    color=C_ERROR,
                                )
                            )
                            return "ended by user"

                reader.cancel()
                await tu.edit(
                    embed=discord.Embed(
                        title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                    ).set_footer(text=footer)
                )
                return result

        listener = asyncio.create_task(listen_for_answer())

        try:
            reader_result = await reader
            if reader_result == "dead":
                listener.cancel()
                return a, "dead"

        except asyncio.CancelledError:  # reader cancelled while being awaited
            return a, await listener

    @commands.command(
        name="tossup",
        description="returns a random tossup",
    )
    async def tossup(self, ctx: Context, *argv) -> None:
        """Play a random tossup."""
        try:
            params = generate_params(argv)
        except ValueError as e:
            await ctx.send(embed=discord.Embed(title=str(e), color=C_ERROR))
            return

        match await self.play_tossup(ctx, params):
            case (answer, "ended by user"):
                await ctx.send(embed=discord.Embed(title="Ending Tossup", color=C_NEUTRAL))

            case (answer, "power"):
                await ctx.send(
                    embed=discord.Embed(title="Power", description=md(answer), color=C_SUCCESS)
                )

            case (answer, "correct"):
                await ctx.send(
                    embed=discord.Embed(title="Correct", description=md(answer), color=C_SUCCESS)
                )

            case (answer, "neg"):
                await ctx.send(
                    embed=discord.Embed(title="Neg", description=md(answer), color=C_ERROR)
                )

            case (answer, "dead"):
                await ctx.send(
                    embed=discord.Embed(
                        title="Incorrect, DT", description=md(answer), color=C_ERROR
                    )
                )

    async def send_tk_end_stats(
        self, ctx: Context, stats: dict[str, int], filters: list[str]
    ) -> None:
        """Send the statistics for a TK session.

        Parameters
        ----------
        ctx : `discord.ext.commands.Context`
            Message context.
        stats : dict[str, int]
            Dictionary of stats.
        filters : list[str]
            List of filters used for the session.
        """
        embed = discord.Embed(title="Session Stats", color=C_NEUTRAL)
        embed.add_field(name="Tossups", value=sum(stats.values()))
        embed.add_field(
            name="Powers/10s/Negs",
            value=f"{stats['power']}/{stats['correct']}/{stats['neg']}",
        )
        embed.add_field(name="Dead Tossups", value=str(stats["dead"]))

        points = stats["power"] * 15 + stats["correct"] * 10 - stats["neg"] * 5

        embed.add_field(name="Points", value=points)

        try:
            embed.add_field(name="PP20TUH", value=round(points / sum(stats.values()) * 20, 2))
        except ZeroDivisionError:
            embed.add_field(
                name="PP20TUH",
                value="wow you really just started a session and ended it immediately",
            )

        embed.add_field(name="Filters", value=f"`{' '.join(filters)}`", inline=False)

        await ctx.send(embed=embed)

    @commands.command(
        name="tk",
        description="start a tk session",
    )
    async def tk(self, ctx: Context, *argv: list[str]) -> None:
        """Start a tk session."""
        try:
            params = generate_params(argv)
        except ValueError as e:
            await ctx.send(embed=discord.Embed(title=str(e), color=C_ERROR))
            return

        tk_stats = {"power": 0, "correct": 0, "neg": 0, "dead": 0}

        while True:
            match await self.play_tossup(ctx, params):
                case (answer, "ended by user"):
                    await self.send_tk_end_stats(ctx, tk_stats, argv)
                    return

                case (answer, "power"):
                    tk_stats["power"] += 1
                    await ctx.send(
                        embed=discord.Embed(title="Power", description=md(answer), color=C_SUCCESS)
                    )

                case (answer, "correct"):
                    tk_stats["correct"] += 1
                    await ctx.send(
                        embed=discord.Embed(
                            title="Correct", description=md(answer), color=C_SUCCESS
                        )
                    )

                case (answer, "neg"):
                    tk_stats["neg"] += 1
                    await ctx.send(
                        embed=discord.Embed(title="Neg", description=md(answer), color=C_ERROR)
                    )

                case (answer, "dead"):
                    tk_stats["dead"] += 1
                    await ctx.send(
                        embed=discord.Embed(
                            title="Incorrect, DT", description=md(answer), color=C_ERROR
                        )
                    )

            try:
                await self.bot.wait_for(
                    "message",
                    check=lambda message: message.author == ctx.author
                    and message.channel == ctx.channel
                    and message.content == f"{ctx.prefix}end",
                    timeout=3.2,
                )  # wait 4 (3.2 + 0.8 at the beggining) seconds to give time to read answer
                await self.send_tk_end_stats(ctx, tk_stats, argv)
                return

            except asyncio.TimeoutError:
                pass

    @commands.command(
        name="tu",
        description="alias for tossup",
    )
    async def tu(self, ctx: Context, *argv) -> None:
        """Alias for `self.tossup()`."""
        await self.tossup(ctx, *argv)


async def setup(bot):  # noqa: D103
    await bot.add_cog(Tossup(bot))
