"""Bonus commands."""

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context
from lib.consts import C_ERROR, C_NEUTRAL, C_SUCCESS, QBREADER_API
from lib.utils import check_answer, generate_params
from markdownify import markdownify as md


class Bonus(commands.Cog, name="bonus commands"):
    """Command class for bonus commands."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def play_bonus(self, ctx: Context, params: dict) -> str | int:
        """Play a bonus question.

        Parameters
        ----------
            ctx : `discord.ext.commands.Context`
                Message context.
            params : `dict`
                Parameters for the API request.

        Returns
        -------
            `str | int`
                `"ended by user"` if the user ended the game, otherwise the number of points.
        """
        async with self.bot.session.post(f"{QBREADER_API}/random-question", json=params) as r:
            bonus = (await r.json(content_type="text/html"))[0]

        points = 0

        leadin = discord.Embed(
            title=bonus["category"]
            if bonus["category"] == bonus["subcategory"]
            else " | ".join([bonus["category"], bonus["subcategory"]]),
            description=bonus["leadin"],
            color=C_NEUTRAL,
        )

        footer = [
            bonus["setName"],
            f"Packet {bonus['packetNumber']}",
            f"Bonus {bonus['questionNumber']}",
            f"Difficulty {bonus['difficulty']}",
        ]

        footer = " | ".join(footer)

        leadin.set_footer(text=footer)
        await ctx.send(embed=leadin)

        try:
            enum = enumerate(zip(bonus["parts"], bonus["formatted_answers"]), 1)
        except KeyError:
            enum = enumerate(zip(bonus["parts"], bonus["answers"]), 1)

        for i, (q, a) in enum:
            part = discord.Embed(title=str(i), description=q, color=C_NEUTRAL)

            await ctx.send(embed=part)

            answer = (
                await self.bot.wait_for(
                    "message",
                    check=lambda message: message.author == ctx.author
                    and message.channel == ctx.channel
                    and not message.content.startswith("_"),
                    timeout=60,
                )
            ).content

            while True:
                if answer.startswith(f"{ctx.prefix}end"):
                    return "ended by user"

                match await check_answer(a, answer, self.bot.session):
                    case ("accept", _):  # correct
                        await ctx.send(
                            embed=discord.Embed(
                                title="Correct", description=md(a), color=C_SUCCESS
                            )
                        )
                        points += 10
                        break

                    case ("reject", _):  # incorrect
                        await ctx.send(
                            embed=discord.Embed(
                                title="Incorrect", description=md(a), color=C_ERROR
                            )
                        )
                        break

                    case ("prompt", response):  # prompt
                        await ctx.send(
                            embed=discord.Embed(
                                title="Prompt",
                                description=md(response) if response else response,
                                color=C_NEUTRAL,
                            )
                        )
                        answer = (
                            await self.bot.wait_for(
                                "message",
                                check=lambda message: message.author == ctx.author
                                and message.channel == ctx.channel
                                and not message.content.startswith("_"),
                                timeout=60,
                            )
                        ).content

                    case _:
                        await ctx.send(
                            embed=discord.Embed(
                                title="Error", description="Something went wrong", color=C_ERROR
                            )
                        )
                        return "ended by user"
                        # i meannnn i could make an error type but this is fine

        return points

    @commands.command(
        name="bonus",
        description="returns a random bonus",
    )
    async def bonus(self, ctx: Context, *argv) -> None:
        """Play a random bonus."""
        try:
            params = generate_params("bonus", argv)
        except ValueError as e:
            await ctx.send(embed=discord.Embed(title=str(e), color=C_ERROR))
            return

        points = await self.play_bonus(ctx, params)

        if points == "ended by user":
            await ctx.send(embed=discord.Embed(title="ending bonus", color=C_NEUTRAL))
            return

        await ctx.send(embed=discord.Embed(title=f"{points}/30", color=C_NEUTRAL))

    @commands.command(
        name="pk",
        description="start a pk session",
    )
    async def pk(self, ctx: Context, *argv) -> None:
        """Start a pk session."""
        try:
            params = generate_params("bonus", argv)
        except ValueError as e:
            await ctx.send(embed=discord.Embed(title=str(e), color=C_ERROR))
            return

        total_points = 0
        total_bonuses = 0

        while True:
            points = await self.play_bonus(ctx, params)

            if points == "ended by user":
                stats = discord.Embed(title="Session Stats", color=C_NEUTRAL)
                stats.add_field(name="Bonuses", value=total_bonuses)
                stats.add_field(name="Points", value=total_points)

                try:
                    stats.add_field(name="PPB", value=round(total_points / total_bonuses, 2))
                except ZeroDivisionError:
                    stats.add_field(
                        name="PPB",
                        value="why would you even start a session just to end it?",
                    )

                stats.add_field(name="Filters", value=f"`{' '.join(argv)}`")

                await ctx.send(embed=stats)
                return

            total_points += points
            total_bonuses += 1

            await ctx.send(embed=discord.Embed(title=f"{points}/30", color=C_NEUTRAL))


async def setup(bot):  # noqa D103
    await bot.add_cog(Bonus(bot))
