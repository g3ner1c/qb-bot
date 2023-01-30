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

    async def play_tossup(self, ctx: Context, params: dict) -> str:

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

            result = ""

            buzz = await self.bot.wait_for(
                "message",
                check=lambda message: message.author == ctx.author
                and message.channel == ctx.channel,
                timeout=60,  # no idea how i should make the tossup go dead yet
            )

            if buzz.content.startswith(">end"):
                read.cancel()
                await tu.edit(
                    embed=discord.Embed(
                        title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                    ).set_footer(text=footer)
                )
                await ctx.send(embed=discord.Embed(title=md(a), color=C_NEUTRAL))
                return "ended by user"

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
                            timeout=8,  # 8 seconds is the time on protobowl
                        )
                    ).content

                except asyncio.TimeoutError:
                    print("no answer")
                    read.cancel()
                    await tu.edit(
                        embed=discord.Embed(
                            title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                        ).set_footer(text=footer)
                    )
                    await ctx.send(embed=discord.Embed(title=md(a), color=C_NEUTRAL))
                    return "no answer"

                while True:

                    if answer.startswith(">end"):
                        read.cancel()
                        await tu.edit(
                            embed=discord.Embed(
                                title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                            ).set_footer(text=footer)
                        )
                        await ctx.send(embed=discord.Embed(title=md(a), color=C_NEUTRAL))
                        return "ended by user"

                    match await check_answer(a, answer, self.bot.session):

                        case "accept":
                            print("correct")
                            print("power possible?", can_power.is_set())
                            if can_power.is_set():
                                result = "power"
                            else:
                                result = "correct"
                            break

                        case "reject":
                            print("incorrect")
                            result = "neg"
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
                                        timeout=8,
                                    )
                                ).content

                            except asyncio.TimeoutError:
                                print("no answer")
                                result = "no answer"
                                break

                read.cancel()
                await tu.edit(
                    embed=discord.Embed(
                        title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                    ).set_footer(text=footer)
                )
                await ctx.send(embed=discord.Embed(title=md(a), color=C_NEUTRAL))
                return result

        listener = asyncio.create_task(listen_for_answer())
        return await listener

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

        match await self.play_tossup(ctx, params):

            case "ended by user":
                await ctx.send(embed=discord.Embed(title="ending tossup", color=C_ERROR))

            case "no answer":
                await ctx.send(embed=discord.Embed(title="no answer", color=C_ERROR))

            case "power":
                await ctx.send(embed=discord.Embed(title="power", color=C_SUCCESS))

            case "correct":
                await ctx.send(embed=discord.Embed(title="correct", color=C_SUCCESS))

            case "neg":
                await ctx.send(embed=discord.Embed(title="neg", color=C_ERROR))

    @commands.command(
        name="tk",
        description="start a tk session",
    )
    async def tk(self, ctx: Context, *argv) -> None:

        try:
            params = generate_params("tossup", argv)
        except ValueError:
            await ctx.send(embed=discord.Embed(title="invalid argument", color=C_ERROR))
            return

        tk_stats = {"power": 0, "correct": 0, "neg": 0, "no answer": 0}

        while True:

            match await self.play_tossup(ctx, params):

                case "ended by user":

                    stats = discord.Embed(title="Session Stats", color=C_NEUTRAL)
                    stats.add_field(name="Tossups", value=sum(tk_stats.values()))
                    stats.add_field(
                        name="Powers/10s/Negs",
                        value=f"{tk_stats['power']}/{tk_stats['correct']}/{tk_stats['neg']}",
                    )
                    stats.add_field(name="No Answer", value=tk_stats["no answer"])

                    points = (
                        tk_stats["power"] * 15 + tk_stats["correct"] * 10 - tk_stats["neg"] * 5
                    )

                    stats.add_field(name="Points", value=points)

                    try:
                        stats.add_field(
                            name="PP20TUH", value=round(points / sum(tk_stats.values()) * 20, 2)
                        )
                    except ZeroDivisionError:
                        stats.add_field(
                            name="PP20TUH",
                            value="wow you really just started a session and ended it immediately",
                        )

                    await ctx.send(embed=stats)
                    return

                case "no answer":
                    tk_stats["no answer"] += 1
                    await ctx.send(embed=discord.Embed(title="no answer", color=C_ERROR))

                case "power":
                    tk_stats["power"] += 1
                    await ctx.send(embed=discord.Embed(title="power", color=C_SUCCESS))

                case "correct":
                    tk_stats["correct"] += 1
                    await ctx.send(embed=discord.Embed(title="correct", color=C_SUCCESS))

                case "neg":
                    tk_stats["neg"] += 1
                    await ctx.send(embed=discord.Embed(title="neg", color=C_ERROR))

            await asyncio.sleep(4)  # wait 4 seconds before next tossup to give time to read answer

    @commands.command(
        name="tu",
        description="alias for tossup",
    )
    async def tu(self, ctx: Context, *argv) -> None:
        await self.tossup(ctx, *argv)


async def setup(bot):
    await bot.add_cog(Tossup(bot))
