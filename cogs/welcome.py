import discord
import os
from discord.ext import commands
import sqlite3
from utility.embed import embed
from utility.embed import field
from utility.button import wb1
from utility.button import wb
from utility.embed import we
import json
# create db if not exists
if not os.path.exists('db/welcome.sql'):
    os.makedirs('db', exist_ok=True)
    with open('db/welcome.sql', 'w') as f:
        pass
# Connect to the database
conn = sqlite3.connect('db/welcome.sql')
# Create a cursor
w = conn.cursor()
#create config.json if not exists
if not os.path.exists('config.json'):
        with open('config.json', 'w') as config_file:
            json.dump({}, config_file)
        print("Created config.json file.")
else:
    pass
#take footer icon from config
with open('config.json', 'r') as f:
    config = json.load(f)
    footer_icon = config['footer_icon']
    if config['footer_icon'] is None:
        print("No footer icon found in config.json file.")
with open('config.json','r') as f:
    config = json.load(f)
    invite_link = config['invite_link']
# Create tables
w.execute('''CREATE TABLE IF NOT EXISTS welcome(
  server_id INTEGER PRIMARY KEY,
  message TEXT,
  channel_id INTEGER,
  role_id INTEGER
)''')
# Different table for dm
w.execute('''CREATE TABLE IF NOT EXISTS dm(
  server_id INTEGER PRIMARY KEY,
  message TEXT
)''')
conn.commit()

# Code starts from here
# Class for the commands
class welcome(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    # Event
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Get the server id
        server_id = member.guild.id
        # Get the welcome message
        w.execute("SELECT message FROM welcome WHERE server_id=?", (server_id))
        result = w.fetchone()
        if result is not None:
            message = result[0]
            # Get the channel id
            w.execute("SELECT channel_id FROM welcome WHERE server_id=?", (server_id))
            channelid = w.fetchone()
            if channelid is not None:
                channel=self.bot.get_channel(channelid[0])
                member.mention=member.mention
                member.count=member.guild.member_count
                member.name=member.name
                member.discriminator=member.discriminator
                member.account_age=member.created_at
                await channel.send(f"{message}")
            #Get the role id
            w.execute("SELECT role_id FROM welcome WHERE server_id=?", (server_id))
            roleid = w.fetchone()
            if roleid is not None:
                role = member.guild.get_role(roleid[0])
                await member.add_roles(role)
            # Get the dm message
            w.execute("SELECT message FROM dm WHERE server_id=?", (server_id))
            dm_message = w.fetchone()
            if dm_message is not None:
                dm_message = dm_message[0]
                member.mention=member.mention
                member.count=member.guild.member_count
                member.name=member.name
                member.discriminator=member.discriminator
                member.account_age=member.created_at
                
                await member.send(f"{dm_message}")
            
    @commands.hybrid_command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, manage_messages=True, embed_links=True)
    async def welcome(self, ctx):
        """Configure the welcome commands setting for your server, /welcome"""
        w.execute("SELECT * FROM welcome WHERE server_id = ?", (ctx.guild.id,))
        data = w.fetchone()
        if data is None:
            d =embed("Welcome configuration","Your Welcome message is not turned on, use `the button below` to turn it on",0xAA4A44)
            await ctx.send(embed=d,view=wb(ctx.author.id))
        if data is not None:
            m=we(ctx.guild.id,"Welcome message smart configuration ",footer_icon,ctx.author.name,ctx.author.avatar.url)
            
            await ctx.send(embed=m,view=wb1(self.bot,ctx.author.id))#,view=wb1)
async def setup(bot)->None:
    await bot.add_cog(welcome(bot))
