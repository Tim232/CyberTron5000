"""
MIT License
Copyright (c) 2020 nizcomix

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
from datetime import datetime as dt
from typing import List

import asyncpg
import discord
from discord.ext.commands import Bot, when_mentioned_or
from discord.ext import tasks

from CyberTron5000 import config, ctx

print(
    r"""
 ______             __                         ________                              _______    ______    ______    ______  
 /      \           |  \                       |        \                  ,,          |       \  /      \  /      \  /      \ 
|  $$$$$$\ __    __ | $$____    ______    ______\$$$$$$$$______    ______   _______  | $$$$$$$ |  $$$$$$\|  $$$$$$\|  $$$$$$\
| $$   \$$|  \  |  \| $$    \  /      \  /      \ | $$  /      \  /      \ |       \ | $$____  | $$$\| $$| $$$\| $$| $$$\| $$
| $$      | $$  | $$| $$$$$$$\|  $$$$$$\|  $$$$$$\| $$ |  $$$$$$\|  $$$$$$\| $$$$$$$\| $$    \ | $$$$\ $$| $$$$\ $$| $$$$\ $$
| $$   __ | $$  | $$| $$  | $$| $$    $$| $$   \$$| $$ | $$   \$$| $$  | $$| $$  | $$ \$$$$$$$\| $$\$$\$$| $$\$$\$$| $$\$$\$$
| $$__/  \| $$__/ $$| $$__/ $$| $$$$$$$$| $$      | $$ | $$      | $$__/ $$| $$  | $$|  \__| $$| $$_\$$$$| $$_\$$$$| $$_\$$$$
 \$$    $$ \$$    $$| $$    $$ \$$     \| $$      | $$ | $$       \$$    $$| $$  | $$ \$$    $$ \$$  \$$$ \$$  \$$$ \$$  \$$$
  \$$$$$$  _\$$$$$$$ \$$$$$$$   \$$$$$$$ \$$       \$$  \$$        \$$$$$$  \$$   \$$  \$$$$$$   \$$$$$$   \$$$$$$   \$$$$$$ 
          |  \__| $$                                                                                                         
           \$$    $$                                                                                                         
            \$$$$$$                                                                                                          
"""
)


class CyberTron5000(Bot):
    def __init__(self):
        super().__init__(**self.config_attrs)
        self.colour = 0x00dcff
        self.prefixes, self._tag_dict, self.global_votes = {}, {}, {}
        self.config = config.config()
        self.start_time = dt.utcnow()
        self.ext = [f"CyberTron5000.cogs.{filename[:-3]}" for filename in os.listdir('cogs') if filename.endswith('.py')]
        self.pg_con = self.loop.run_until_complete(self.create_db_pool())
        self.load_extension(name='jishaku')
        for task in (self.startup, self._init_tags):
            self.loop.create_task(task())
        self.logging = dict(
            invite='https://discord.com/oauth2/authorize?client_id=697678160577429584&scope=bot&permissions=104189632',
            support='https://discord.com/invite/2fxKxJH', github='https://github.com/niztg/CyberTron5000',
            website='https://cybertron-5k.netlify.app', reddit='https://reddit.com/r/CyberTron5000',
            servers={"CyberTron5000 Emotes 1": "https://discord.gg/29vqZfm",
                     "CyberTron5000 Emotes 2": "https://discord.gg/Qn7VYg8",
                     "CyberTron5000 Emotes 3": "https://discord.gg/Xgddz6W"})

    @property
    def owner(self) -> discord.User:
        return self.get_user(350349365937700864)

    @property
    def logging_channel(self) -> List[discord.TextChannel]:
        return [self.get_channel(727277234666078220), self.get_channel(746935543144644650),
                self.get_channel(746935661201981510)]

    @property
    def uptime(self) -> dict:
        delta_uptime = dt.utcnow() - self.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}

    @property
    def config_attrs(self) -> dict:
        return {
            'command_prefix': self.get_prefix,
            'pm_help': None,
            'allowed_mentions': discord.AllowedMentions(users=False, roles=False, everyone=False),
            'case_insensitive': True,
            'status': discord.Status.online
        }

    async def create_db_pool(self):
        return await asyncpg.create_pool(user=self.config.pg_data["user"], password=self.config.pg_data["password"],
                                         database=self.config.pg_data["db"])

    async def get_prefix(self, message):
        if not message.guild:
            return 'c$'
        DEFAULT_PREFIX = ["c$"]
        prefixes = self.prefixes.get(message.guild.id, DEFAULT_PREFIX)
        if message.author.id == self.owner.id:
            return when_mentioned_or(*prefixes, 'dev ')(self, message)
        return when_mentioned_or(*prefixes)(self, message)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or ctx.CyberContext)

    def run(self, *args, **kwargs):
        super().run(self.config.bot_token)

    @tasks.loop(minutes=3)
    async def loop(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                             name=f"{len(self.users):,} users in {len(self.guilds):,} guilds"))

    async def startup(self):
        await self.wait_until_ready()
        print(f"{self.user.name.upper()} IS ONLINE")
        for file in self.ext:
            try:
                self.load_extension(name=file)
            except Exception as error:
                print(f"Could not load {file}: {error}")
        print(f"COGS HAVE BEEN LOADED")
        prefix_data = await self.pg_con.fetch("SELECT guild_id, array_agg(prefix) FROM prefixes GROUP BY guild_id")
        for entry in prefix_data:
            self.prefixes[entry['guild_id']] = entry['array_agg']
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                             name=f"{len(self.users):,} users in {len(self.guilds):,} guilds"))
        print("PREFIXES AND PRESENCE SETUP")
        print("READY!")
        print(
            "──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────")

    async def _init_tags(self):
        await self.wait_until_ready()
        SQL = """
        SELECT guild_id FROM tags
        """
        tags = await self.pg_con.fetch(SQL)
        for query in tags:
            self._tag_dict[query['guild_id']] = {}
            tags2 = await self.pg_con.fetch("""SELECT name, content, uses, user_id, id FROM tags WHERE guild_id = $1""",
                                            query['guild_id'])
            for query2 in tags2:
                self._tag_dict[query['guild_id']][query2['name']] = {'content': query2['content'],
                                                                     'uses': query2['uses'] or 0,
                                                                     'author': query2['user_id'], 'id': query2['id']}
        print("TAGS HAVE BEEN INITIALIZED")
        print(self._tag_dict)


CyberTron5000().run()
