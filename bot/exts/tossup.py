"""Tossup commands."""

import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context
from lib.consts import API_RANDOM_QUESTION, C_ERROR, C_NEUTRAL, C_SUCCESS
from lib.utils import check_answer, generate_params, tossup_read
from markdownify import markdownify as md

lock = asyncio.Lock()


class Tossup(commands.Cog, name="tossup commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="tossup",
        description="returns a random tossup",
    )
    async def tossup(self, ctx: Context, *argv) -> None:

        try:
            params = generate_params("tossup", argv)
        except ValueError:
            await ctx.send(embed=discord.Embed(title="invalid argument", color=C_ERROR))
            return

        async with self.bot.session.post(API_RANDOM_QUESTION, json=params) as r:
            tossup = (await r.json(content_type="text/html"))[0]

        tossup_parts = tossup_read(tossup["question"], 5)

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

        print("power possible?", can_power.is_set())

        embed = discord.Embed(title="Tossup", description="", color=C_NEUTRAL)

        embed.set_footer(text=footer)
        tu = await ctx.send(embed=embed)

        try:
            a = tossup["formatted_answer"]
        except KeyError:
            a = tossup["answer"]

        print(tossup["answer"])

        async def edit_tossup():  # reader task

            for part in tossup_parts:

                async with lock:

                    embed = discord.Embed(title="Tossup", description=part, color=C_NEUTRAL)
                    embed = embed.set_footer(text=footer)
                    await tu.edit(embed=embed)
                    if can_power.is_set() and "*" in part:
                        print("power mark read")

                        can_power.clear()
                        print("power possible?", can_power.is_set())

                await asyncio.sleep(0.8)

        read = asyncio.create_task(edit_tossup())

        async def listen_for_answer():  # buzzer task

            await self.bot.wait_for(
                "message",
                check=lambda message: message.author == ctx.author
                and message.channel == ctx.channel
                and not message.content.startswith("_"),
            )

            async with lock:

                print("buzz")

                await ctx.send(
                    embed=discord.Embed(
                        title="Buzz",
                        description=f"from {ctx.author.mention}",
                        color=C_SUCCESS,
                    )
                )

                try:
                    answer = (
                        await self.bot.wait_for(
                            "message",
                            check=lambda message: message.author == ctx.author
                            and message.channel == ctx.channel,
                            timeout=5,
                        )
                    ).content

                except asyncio.TimeoutError:
                    await ctx.send(embed=discord.Embed(title="no answer", color=C_ERROR))
                    print("no answer")
                    read.cancel()
                    await tu.edit(
                        embed=discord.Embed(
                            title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                        ).set_footer(text=footer)
                    )
                    await ctx.send(embed=discord.Embed(title=md(a), color=C_NEUTRAL))
                    return

                while True:

                    match await check_answer(a, answer, self.bot.session):

                        case "accept":
                            await ctx.send(embed=discord.Embed(title="correct", color=C_SUCCESS))
                            print("correct")
                            print("power possible?", can_power.is_set())
                            if can_power.is_set():
                                await ctx.send(
                                    embed=discord.Embed(
                                        title="power",
                                        color=C_SUCCESS,
                                    )
                                )
                            break

                        case "reject":
                            await ctx.send(embed=discord.Embed(title="incorrect", color=C_ERROR))
                            print("incorrect")
                            break

                        case "prompt":
                            await ctx.send(embed=discord.Embed(title="prompt", color=C_NEUTRAL))
                            print("prompt")

                            try:
                                answer = (
                                    await self.bot.wait_for(
                                        "message",
                                        check=lambda message: message.author == ctx.author
                                        and message.channel == ctx.channel,
                                        timeout=5,
                                    )
                                ).content

                            except asyncio.TimeoutError:
                                await ctx.send(
                                    embed=discord.Embed(title="no answer", color=C_ERROR)
                                )
                                print("no answer")
                                break

                read.cancel()
                await tu.edit(
                    embed=discord.Embed(
                        title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                    ).set_footer(text=footer)
                )
                await ctx.send(embed=discord.Embed(title=md(a), color=C_NEUTRAL))
                return

        asyncio.create_task(listen_for_answer())

    @commands.command(
        name="tu",
        description="alias for tossup",
    )
    async def tu(self, ctx: Context, *argv) -> None:
        await self.tossup(ctx, *argv)


async def setup(bot):
    await bot.add_cog(Tossup(bot))
