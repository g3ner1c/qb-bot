"""Bonus commands."""

from typing import Union

import discord
from discord.ext import commands
from discord.ext.commands import Context
from lib.consts import API_RANDOM_QUESTION, C_ERROR, C_NEUTRAL, C_SUCCESS
from lib.utils import check_answer, generate_params
from markdownify import markdownify as md


class Bonus(commands.Cog, name="bonus commands"):
    def __init__(self, bot):
        self.bot = bot

    async def play_bonus(self, ctx: Context, params: dict) -> Union[str, int]:

        async with self.bot.session.post(API_RANDOM_QUESTION, json=params) as r:
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

                if answer.startswith(">end"):
                    return "user ended bonus"

                match await check_answer(a, answer, self.bot.session):

                    case "accept":  # correct
                        await ctx.send(
                            embed=discord.Embed(
                                title="Correct", description=md(a), color=C_SUCCESS
                            )
                        )
                        points += 10
                        break

                    case "reject":  # incorrect
                        await ctx.send(
                            embed=discord.Embed(
                                title="Incorrect", description=md(a), color=C_ERROR
                            )
                        )
                        break

                    case "prompt":  # prompt
                        await ctx.send(embed=discord.Embed(title="Prompt", color=C_NEUTRAL))
                        answer = (
                            await self.bot.wait_for(
                                "message",
                                check=lambda message: message.author == ctx.author
                                and message.channel == ctx.channel
                                and not message.content.startswith("_"),
                                timeout=60,
                            )
                        ).content

        return points

    @commands.command(
        name="bonus",
        description="returns a random bonus",
    )
    async def bonus(self, ctx: Context, *argv) -> None:

        try:
            params = generate_params("bonus", argv)
        except ValueError:
            await ctx.send(embed=discord.Embed(title="invalid argument", color=C_ERROR))
            return

        points = await self.play_bonus(ctx, params)

        if points == "user ended bonus":
            await ctx.send(embed=discord.Embed(title="ending bonus", color=C_NEUTRAL))
            return

        await ctx.send(embed=discord.Embed(title=f"{points}/30", color=C_NEUTRAL))

    @commands.command(
        name="pk",
        description="start a pk session",
    )
    async def pk(self, ctx: Context, *argv) -> None:

        try:
            params = generate_params("bonus", argv)
        except ValueError:
            await ctx.send(embed=discord.Embed(title="invalid argument", color=C_ERROR))
            return

        total_points = 0
        total_bonuses = 0

        while True:

            points = await self.play_bonus(ctx, params)

            if points == "user ended bonus":

                stats = discord.Embed(title="Session Stats", color=C_NEUTRAL)
                stats.add_field(name="Bonuses", value=total_bonuses)
                stats.add_field(name="Points", value=total_points)
                stats.add_field(name="PPB", value=round(total_points / total_bonuses, 2))
                await ctx.send(embed=stats)
                return

            total_points += points
            total_bonuses += 1

            await ctx.send(embed=discord.Embed(title=f"{points}/30", color=C_NEUTRAL))

    @commands.command(
        name="end",
        description="ends a pk session or a bonus set",
    )
    async def end(self, ctx: Context) -> None:
        # doesnt do anything just makes it look neat on >help
        pass


async def setup(bot):
    await bot.add_cog(Bonus(bot))
