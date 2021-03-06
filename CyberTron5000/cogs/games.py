import asyncio
import random

import aiohttp
import aiotrivia
import discord
from discord.ext import commands
from unidecode import unidecode as u

from CyberTron5000.utils import (
    cyberformat,
    lists
)


class Games(commands.Cog):
    """Games!"""

    def __init__(self, bot):
        self.bot = bot
        self.daggy = 491174779278065689

    # rock paper scissors, shoot

    @commands.command(aliases=['rps'], help="Rock paper scissors shoot")
    async def rockpaperscissors(self, ctx):
        rps_dict = {
            "🗿": {
                "🗿": "draw",
                "📄": "lose",
                "✂": "win"
            },
            "📄": {
                "🗿": "win",
                "📄": "draw",
                "✂": "lose"
            },
            "✂": {
                "🗿": "lose",
                "📄": "win",
                "✂": "draw"
            }
        }
        choice = random.choice([*rps_dict.keys()])
        msg = await ctx.send(embed=discord.Embed(colour=self.bot.colour, description=f"**Choose one 👇**").set_footer(
            text=f"You have 15 seconds."))
        for r in rps_dict.keys():
            await msg.add_reaction(r)
        try:
            r, u = await self.bot.wait_for('reaction_add', timeout=15, check=lambda re, us: us == ctx.author and str(
                re) in rps_dict.keys() and re.message.id == msg.id)
            play = rps_dict.get(str(r.emoji))
            await msg.edit(embed=discord.Embed(colour=self.bot.colour,
                                               description=f"Result: **{play[choice].title()}**\nI Played: **{choice}**\nYou Played: **{str(r.emoji)}**"))
        except asyncio.TimeoutError:
            await ctx.send(f"Boo, you ran out of time!")

    # kiss marry kill command

    @commands.command(help="Kiss, marry, kill.", aliases=['kmk'])
    async def kissmarrykill(self, ctx):
        member1 = random.choice(ctx.guild.members)
        member2 = random.choice(ctx.guild.members)
        member3 = random.choice(ctx.guild.members)
        if member1 == member2:
            member1 = random.choice(ctx.guild.members)
        elif member3 == member2:
            member3 = random.choice(ctx.guild.members)
        members = [member1, member2, member3]
        kmk = {'😘': 'kiss (😘)', '👫': 'marry (👫)', '🔪': 'kill(🔪)'}
        embed = discord.Embed(colour=self.bot.colour)
        embed.add_field(name=member1.display_name, value="\u200b")
        embed.add_field(name=member2.display_name, value="\u200b")
        embed.add_field(name=member3.display_name, value="\u200b")
        embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)

        async def _add_reactions(_msg, _reactions):
            for r in _reactions:
                await _msg.add_reaction(r)

        initial_len = len(kmk)
        while len(kmk) > 1:
            index = initial_len - len(kmk)
            ask_kmk = ', '.join(kmk.values())
            embed.description = f"**Would you {ask_kmk} {members[index].display_name}?**"
            msg = await ctx.send(embed=embed)
            self.bot.loop.create_task(_add_reactions(msg, kmk))

            def check(reaction, user):
                return str(reaction.emoji) in kmk and user == ctx.author and reaction.message.id == msg.id

            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("Didn't respond in time")
            embed.set_field_at(index, name=members[index].display_name, value=str(reaction.emoji))
            kmk.pop(str(reaction.emoji))

        if len(kmk) != 1:
            print('error')
        embed.description = '**Results**'
        index = initial_len - len(kmk)
        embed.set_field_at(index, name=members[index].display_name, value=kmk.popitem()[0])
        await ctx.send(embed=embed)

    @commands.group(aliases=['wtp'], invoke_without_command=True)
    async def whosthatpokemon(self, ctx):
        """
        Who's that pokemon!?
        """
        dutchy = self.bot.get_user(171539705043615744) or await self.bot.fetch_user(171539705043615744)
        daggy = self.bot.get_user(self.daggy) or await self.bot.fetch_user(self.daggy)
        async with ctx.typing():
            resp = {'token': self.bot.config.dagpi_token}
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://dagpi.tk/api/wtp', headers=resp) as r:
                    resp = await r.json()
                pokemon = resp['pokemon']
                async with cs.get(f"https://some-random-api.ml/pokedex?pokemon={u(pokemon['name']).lower()}") as r:
                    res = await r.json()
                await cs.close()
            evo_line = []
            for e in res[0]['family']['evolutionLine']:
                if str(e).lower() == pokemon['name'].lower():
                    evo_line.append("???")
                else:
                    evo_line.append(e)
            embed = discord.Embed(colour=self.bot.colour)
            embed.set_image(url=resp['question_image'])
            embed.set_footer(
                text=f"Much thanks to {str(daggy)} for this amazing API, and {str(dutchy)} for the wonderful idea!")
            embed.title = "Who's that Pokémon?"
            embed.description = f"You have 3 attempts | You have 30 seconds\nYou can ask for a hint by doing `{ctx.prefix}hint`, or cancel by doing `{ctx.prefix}cancel`!"
            await ctx.send(embed=embed)
            dashes = cyberformat.better_random_char(pokemon['name'], '_')
            hints = [
                discord.Embed(colour=self.bot.colour, title="Types", description=', '.join(pokemon['type'])),
                discord.Embed(title=f"`{dashes}`", colour=self.bot.colour),
                discord.Embed(colour=self.bot.colour, title="Evolution Line", description=" → ".join(evo_line)),
                discord.Embed(title="Pokédex Entry", description=res[0]['description'].lower().replace(pokemon['name'].lower(), "???"), colour=self.bot.colour),
                discord.Embed(colour=self.bot.colour, title="Species", description=" ".join(res[0]['species']))
            ]
        try:
            for x in range(3):
                msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=30.0)
                if msg.content.lower() == str(resp['pokemon']['name']).lower():
                    embed = discord.Embed(title=f"Correct! The answer was {resp['pokemon']['name']}", colour=self.bot.colour)
                    embed.set_image(url=resp['answer_image'])
                    return await ctx.send(embed=embed)
                elif msg.content.lower().startswith(f"{ctx.prefix}hint"):
                    await ctx.send(embed=random.choice(hints))
                    continue
                elif msg.content.lower().startswith(f"{ctx.prefix}cancel"):
                    embed = discord.Embed(title=f"{resp['pokemon']['name']}", colour=self.bot.colour)
                    embed.set_image(url=resp['answer_image'])
                    embed.set_author(name="The correct answer was....")
                    return await ctx.send(embed=embed)
                else:
                    continue
            embed = discord.Embed(title=f"{resp['pokemon']['name']}", colour=self.bot.colour)
            embed.set_image(url=resp['answer_image'])
            embed.set_author(name="Incorrect! The correct answer was....")
            return await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            embed = discord.Embed(title=f"{resp['pokemon']['name']}", colour=self.bot.colour)
            embed.set_image(url=resp['answer_image'])
            embed.set_author(name="You ran out of time! The answer was...")
            return await ctx.send(embed=embed)

    @commands.command(help="Get's you a trivia question.", aliases=['tr', 't'])
    async def trivia(self, ctx, difficulty: str = None):
        trivia = aiotrivia.TriviaClient()
        difficulty = difficulty or random.choice(['easy', 'medium', 'hard'])
        try:
            question = await trivia.get_random_question(difficulty)
        except aiotrivia.AiotriviaException:
            return await ctx.send(f'**{difficulty}** is not a valid difficulty!')
        embed = discord.Embed(colour=ctx.bot.colour)
        embed.title = question.question
        responses = question.responses
        random.shuffle(responses)
        embed.description = "\n".join(
            [f':regional_indicator_{lists.NUMBER_ALPHABET[i].lower()}: **{v}**' for i, v in enumerate(responses, 1)])
        embed.add_field(name="Info",
                        value=f'Difficulty: **{question.difficulty.title()}**\nCategory: **{question.category}**')
        embed.set_footer(text="React with the correct answer! | You have 15 seconds")
        emojis = [cyberformat.to_emoji(x) for x in range(len(responses))]
        index = responses.index(question.answer)
        msg = await ctx.send(embed=embed)
        await trivia.close()
        for e in emojis:
            await msg.add_reaction(e)

        def check(reaction: discord.Reaction, user: discord.User):
            return reaction.message.id == msg.id and user.id == ctx.author.id and str(reaction.emoji) in emojis

        correct = emojis[index]

        try:
            r, u = await self.bot.wait_for('reaction_add', check=check, timeout=15)
            if str(r.emoji) == correct:
                await msg.edit(embed=discord.Embed(colour=self.bot.colour,
                                                   description=f"{ctx.tick()} Correct! The answer was {correct}, **{question.answer}**"))
            else:
                await msg.edit(embed=discord.Embed(colour=self.bot.colour,
                                                   description=f"{ctx.tick(False)} Incorrect! The correct answer was {correct}, **{question.answer}**"))
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(colour=self.bot.colour,
                                               description=f"{ctx.tick(False)} You ran out of time! The correct answer was {correct}, **{question.answer}**"))

    @commands.group(aliases=['gl', 'gtl'], invoke_without_command=True)
    async def guesslogo(self, ctx):
        """
        Guess a random logo!
        """
        daggy = self.bot.get_user(self.daggy) or await self.bot.fetch_user(self.daggy)
        async with ctx.typing():
            resp = {'token': self.bot.config.dagpi_token}
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://dagpi.tk/api/logogame', headers=resp) as r:
                    resp = await r.json()
            easy = bool(resp['easy'])
            hard = not easy
            await cs.close()
            embed = discord.Embed(
                title="Which company is this?", colour=self.bot.colour).set_image(
                url=resp['question']).set_footer(
                text=f"Much thanks to {str(daggy)} for this amazing API!", icon_url=daggy.avatar_url)
            embed.add_field(name=f'**Difficulty**', value=f'{ctx.tick(easy)} **Easy?**\n{ctx.tick(hard)} **Hard?**')
            try:
                embed.add_field(name="**Company Description**", value=resp['clue'])
            except KeyError:
                pass
            embed.description = f"Do `{ctx.prefix}hint` to see a hint, or `{ctx.prefix}cancel` to cancel."
            await ctx.send(embed=embed)
        try:
            for x in range(3):
                msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and not m.author.bot,
                                              timeout=30.0)
                if msg.content.lower() == str(resp['brand']).lower():
                    embed = discord.Embed(title=f"Correct! The answer was {resp['brand']}",
                                          colour=self.bot.colour)
                    embed.set_image(url=resp['answer'])
                    return await ctx.send(embed=embed)
                elif msg.content.lower().startswith(f"{ctx.prefix}hint"):
                    embed = discord.Embed(title=f"`{resp['hint']}`",
                                          colour=self.bot.colour)
                    await ctx.send(embed=embed)
                    continue
                elif msg.content.lower().startswith(f"{ctx.prefix}cancel"):
                    embed = discord.Embed(title=f"The answer was {resp['brand']}",
                                          colour=self.bot.colour)
                    embed.set_image(url=resp['answer'])
                    return await ctx.send(embed=embed)
                else:
                    continue
            embed = discord.Embed(title=f"The answer was {resp['brand']}",
                                  colour=self.bot.colour)
            embed.set_image(url=resp['answer'])
            return await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            embed = discord.Embed(title=f"{resp['brand']}", colour=self.bot.colour)
            embed.set_image(url=resp['answer'])
            embed.set_author(name="You ran out of time! The answer was...")
            return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
