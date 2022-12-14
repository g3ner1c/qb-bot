import discord
import requests
from discord.ext import commands
from discord.ext.commands import Context
from lib.consts import C_ERROR, C_NEUTRAL, C_SUCCESS
from lib.utils import parse_int_range, parse_subcats
from markdownify import markdownify as md


class Bonus(commands.Cog, name="bonus commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="bonus",
        description="returns a random bonus",
    )
    async def bonus(self, context: Context, *argv) -> None:

        api = "https://www.qbreader.org/api/random-question"

        params = {"questionType": "bonus"}

        diffs = []
        cats = []

        for arg in argv:

            if arg.isdigit():
                diffs.append(arg)

            elif arg.isalpha():
                cats.append(arg)

            else:
                await context.send(embed=discord.Embed(title="invalid argument", color=C_ERROR))
                return

        if diffs:
            params["difficulties"] = parse_int_range(diffs)

        if cats:
            params["subcategories"] = parse_subcats(cats)

        bonus = requests.post(api, json=params).json()[0]

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

        # if bonus["subcategory"] != bonus["category"]:
        #     footer.append(bonus["subcategory"])

        footer = " | ".join(footer)

        leadin.set_footer(text=footer)
        await context.send(embed=leadin)

        try:
            enum = enumerate(zip(bonus["parts"], bonus["answers"], bonus["formatted_answers"]), 1)
        except KeyError:
            enum = enumerate(zip(bonus["parts"], bonus["answers"], bonus["answers"]), 1)

        for i, (q, a, fa) in enum:

            part = discord.Embed(title=str(i), description=q, color=C_NEUTRAL)

            await context.send(embed=part)

            while True:

                answer = await self.bot.wait_for(
                    "message",
                    check=lambda message: message.author == context.author
                    and message.channel == context.channel,
                    timeout=60,
                )

                # dont interpret as answer if message starts with _
                if not answer.content.startswith("_"):
                    break

            if answer.content.startswith(">end"):
                await context.send(embed=discord.Embed(title="ending bonus", color=C_NEUTRAL))
                return

            if answer.content.lower() in a.lower():  # correct
                await context.send(
                    embed=discord.Embed(title="Correct", description=md(fa), color=C_SUCCESS)
                )
                points += 10

            else:  # incorrect
                await context.send(
                    embed=discord.Embed(title="Incorrect", description=md(fa), color=C_ERROR)
                )

        await context.send(
            embed=discord.Embed(title=f"{points}/{10*len(bonus['parts'])}", color=C_NEUTRAL)
        )

    @commands.command(
        name="pk",
        description="start a pk session",
    )
    async def pk(self, context: Context, *argv) -> None:

        api = "https://www.qbreader.org/api/random-question"

        params = {"questionType": "bonus"}

        diffs = []
        cats = []

        for arg in argv:

            if arg.isdigit():
                diffs.append(arg)

            elif arg.isalpha():
                cats.append(arg)

            else:
                await context.send(embed=discord.Embed(title="invalid argument", color=C_ERROR))
                return

        if diffs:
            params["difficulties"] = parse_int_range(diffs)

        if cats:
            params["subcategories"] = parse_subcats(cats)

        total_points = 0
        total_bonuses = 0

        while True:

            bonus = requests.post(api, json=params).json()[0]

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

            # if bonus["subcategory"] != bonus["category"]:
            #     footer.append(bonus["subcategory"])

            footer = " | ".join(footer)

            leadin.set_footer(text=footer)
            await context.send(embed=leadin)

            try:
                enum = enumerate(
                    zip(bonus["parts"], bonus["answers"], bonus["formatted_answers"]), 1
                )
            except KeyError:
                enum = enumerate(zip(bonus["parts"], bonus["answers"], bonus["answers"]), 1)

            for i, (q, a, fa) in enum:

                part = discord.Embed(title=str(i), description=q, color=C_NEUTRAL)

                await context.send(embed=part)

                while True:

                    answer = await self.bot.wait_for(
                        "message",
                        check=lambda message: message.author == context.author
                        and message.channel == context.channel,
                        timeout=60,
                    )

                    # dont interpret as answer if message starts with _
                    if not answer.content.startswith("_"):
                        break

                if answer.content.startswith(">end"):
                    stats = discord.Embed(title="Session Stats", color=C_NEUTRAL)
                    stats.add_field(name="Bonuses", value=total_bonuses)
                    stats.add_field(name="Points", value=total_points)
                    stats.add_field(name="PPB", value=round(total_points / total_bonuses, 2))
                    await context.send(embed=stats)
                    break

                if answer.content.lower() in a.lower():  # correct
                    await context.send(
                        embed=discord.Embed(title="Correct", description=md(fa), color=C_SUCCESS)
                    )
                    points += 10
                    total_points += 10

                else:  # incorrect
                    await context.send(
                        embed=discord.Embed(title="Incorrect", description=md(fa), color=C_ERROR)
                    )

            else:
                total_bonuses += 1
                await context.send(
                    embed=discord.Embed(
                        title=f"{points}/{10*len(bonus['parts'])}", color=C_NEUTRAL
                    )
                )
                continue

            break

    @commands.command(
        name="end",
        description="ends a pk session or a bonus set",
    )
    async def end(self, context: Context) -> None:
        # doesnt do anything just makes it look neat on >help
        pass


async def setup(bot):
    await bot.add_cog(Bonus(bot))
