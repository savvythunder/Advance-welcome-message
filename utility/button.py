import asyncio
import aiohttp
import contextlib
import discord
from discord.ext import commands
from discord import ui
import sqlite3
from .embed import we,embed
from utility.embed_builder import BaseView
import json
# fucntion to create button easily.
def button(label,style,custom_id=None,emoji=None):
    return discord.ui.Button(label=label,style=style,custom_id=custom_id,emoji=emoji)
# welcome.py buttons
welcome = sqlite3.connect('db/welcome.sql')
cursor = welcome.cursor()

with open('config.json', 'r') as f:
    config = json.load(f)
    footer_icon = config['footer_icon']

class wb(ui.View):
    def __init__(self, userid):
        super().__init__()
        self.userid = userid

    @ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction, button):
        if interaction.user.id == self.userid:
            cursor.execute("INSERT INTO welcome(server_id,message,channel_id,role_id) VALUES(?,?,?,?)",(interaction.guild.id,"Welcome {member.mention} to {guild.name}","None","None"))
            welcome.commit()
            await interaction.message.delete()
            j = we(interaction.guild.id, "Welcome message is now enabled", footer_icon, interaction.user.name, interaction.user.avatar.url)
            await interaction.response.send_message(embed=j)
        else:
            f = we(interaction.guild.id, "Welcome message is already enabled", footer_icon, interaction.user.name, interaction.user.avatar.url)
            await interaction.message.delete()
            await interaction.response.send_message(embed=f)

class wb1(ui.View):
    def __init__(self, bot,userid):
        super().__init__()
        self.userid = userid
        self.bot = bot
    @ui.button(label="Change Channel", style=discord.ButtonStyle.blurple)
    async def button_callback(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.message.delete()
            await interaction.response.send_message("please select the channel from the drop down below",view=ChannelSelect(self.bot,self.userid,interaction.guild.id))
    @ui.button(label="Change Role", style=discord.ButtonStyle.blurple)
    async def button_callback1(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.message.delete()
            await interaction.response.send_message("please select the role from the drop down below",view=RoleSelectview(self.bot,self.userid,interaction.guild.id))
    @ui.button(label="Change Message", style=discord.ButtonStyle.blurple)
    async def button_callback2(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.message.delete()
            session = aiohttp.ClientSession()
            view = BaseView(interaction, session, "gen")
            await interaction.response.send_message(view.content, view = view)
            message = await interaction.original_response()
            view.set_message(message)
            await view.wait()

    @ui.button(label="Test",style=discord.ButtonStyle.success)
    async def button_callback4(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.message.delete()
            await interaction.response.send_message("Please select the channel from the drop down below",view=channelselectm(self.bot,self.userid,interaction.guild.id))
#channel selectm
class drop_down(ui.ChannelSelect):
    def __init__(self, bot,userid,guildid):
        super().__init__(placeholder="Select a channel", min_values=1, max_values=1)
        self.bot = bot
        self.userid = userid
        self.guildid = guildid

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.userid:
            await interaction.response.send_message(f"You selected: {self.values[0].mention}")
            channel=self.values[0].id
            # get the message from the database
            cursor.execute("SELECT message FROM welcome WHERE server_id = ?", (interaction.guild.id,))
            messagejson=cursor.fetchone()
            #send the message
            if messagejson is None:
                await interaction.channel.send("Welcome message is not set")
            if messagejson is not None:
                # Get the channel
                x = self.bot.get_channel(channel)
                # Read the json
                messagejson = json.loads(messagejson[0])
                # Convert the json to a discord message
                content=messagejson["content"]
            embeds=messagejson["embeds"]
            eembeds=[]
            for embed in embeds:
                embeds=discord.Embed.from_dict(embed)
                eembeds.append(embeds)
                channel=self.values[0].id
                chanel=self.bot.get_channel(channel)
                
                content=messagejson["content"]
                await chanel.send(content=content,embeds=eembeds)
# channelselectm view
class channelselectm(ui.View):
    def __init__(self, bot,userid,guildid):
        super().__init__()
        self.bot = bot
        self.userid = userid
        self.guildid = guildid
        self.add_item(drop_down(self.bot,self.userid,self.guildid))
#create a drop down menu of ChannelSelect
class dropdown(ui.ChannelSelect):
    def __init__(self, bot,userid,guildid):
        super().__init__(placeholder="Select a channel", min_values=1, max_values=1)
        self.bot = bot
        self.userid = userid
        self.guildid = guildid
    #dropdown's call back function
    async def callback(self, interaction):
        
        if interaction.user.id == self.userid:
            try:
                cursor.execute("UPDATE welcome SET channel_id = ? WHERE server_id = ?",(self.values[0].id,self.guildid))
                welcome.commit()
                await interaction.message.delete()
                m=we(interaction.guild.id,"Welcome message smart configuration ",footer_icon,interaction.user.name, interaction.user.avatar.url)
                m.set_footer(text=f"Welcome channel has been changed to {self.values[0].name}")
                await interaction.response.send_message(embed=m,view=wb1(self.bot,self.userid))
            except Exception as e:
                #insert into db because if channel is not found it will throw an error
                cursor.execute("INSERT INTO welcome(server_id,message,channel_id,role_id) VALUES(?,?,?,?)",(self.guildid,"Welcome {member.mention} to {guild.name}",str(self.values[0].id),"None"))
                
                await interaction.message.delete()
                m=we(interaction.guild_id,"Welcome message smart configuration ",footer_icon,interaction.user.name, interaction.user.avatar)
                m.set_footer(text=f"Welcome channel has been changed to {self.values[0].name}")
                await interaction.response.send_message(embed=m,view=wb1(self.bot,self.userid))
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
            
class ChannelSelect(ui.View):
    def __init__(self, bot,userid,guildid):
        super().__init__()
        self.bot = bot
        self.userid = userid
        self.guildid = guildid
        self.add_item(dropdown(self.bot,self.userid,self.guildid))
class Roleselect(ui.RoleSelect):
    def __init__(self, bot,userid,guildid):
        super().__init__(placeholder="Select a role", min_values=1, max_values=1)
        self.bot = bot
        self.userid = userid
        self.guildid = guildid
    #dropdown's call back function
    async def callback(self, interaction):
        if interaction.user.id == self.userid:
            try:
                cursor.execute("UPDATE welcome SET role_id = ? WHERE server_id = ?",(self.values[0].id,self.guildid))
                welcome.commit()
                await interaction.message.delete()
                m=we(interaction.guild.id,"Welcome message smart configuration ",footer_icon,interaction.user.name, interaction.user.avatar.url)
                m.set_footer(text=f"Welcome role has been changed to {self.values[0].name}")
                await interaction.response.send_message(embed=m,view=wb1(self.bot,self.userid))
            except Exception as e:
                cursor.executemany("INSERT INTO welcome(server_id,message,channel_id,role_id) VALUES(?,?,?,?)",(self.guildid,"Welcome {member.mention} to {guild.name}","None",str(self.values[0].id)))
                await interaction.message.delete()
                m=we(interaction.guild_id,"Welcome message smart configuration ",footer_icon,interaction.user.name, interaction.user.avatar)
                m.set_footer(text=f"Welcome role has been changed to {self.values[0].name}")
                await interaction.response.send_message(embed=m,view=wb1(self.bot,self.userid))
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
class RoleSelectview(ui.View):
    def __init__(self, bot,userid,guildid):
        super().__init__()
        self.bot = bot
        self.userid = userid
        self.guildid = guildid
        self.add_item(Roleselect(self.bot,self.userid,self.guildid))
#Embed builder to edit the embed of the welcome message
class EmbedBuilder(ui.View):
    def __init__(self, bot,userid,guildid,embed):
        super().__init__()
        self.bot = bot
        self.userid = userid
        self.guildid = guildid
        self.embed = embed
    @ui.button(label="Title", style=discord.ButtonStyle.blurple)
    async def button_callbacks(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.response.send_message("Please enter the title of the embed",ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                self.embed.title = msg.content
                await interaction.message.edit(embed=self.embed)
                await msg.delete(delay=0.1)
            except asyncio.TimeoutError:
                await interaction.response.send_message("You took too long to respond!",ephemeral=True)
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
    @ui.button(label="Description", style=discord.ButtonStyle.blurple)
    async def button_callback1(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.response.send_message("Please enter the description of the embed",ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                self.embed.description = msg.content
                await interaction.message.edit(embed=self.embed)
                await msg.delete(delay=0.1)
            except asyncio.TimeoutError:
                await interaction.response.send_message("You took too long to respond!",ephemeral=True)
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
    @ui.button(label="Footer", style=discord.ButtonStyle.blurple)
    async def button_callback2(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.response.send_message("Please enter the footer of the embed",ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                self.embed.set_footer(text=msg.content)
                await interaction.message.edit(embed=self.embed)
                await msg.delete(delay=0.1)
            except asyncio.TimeoutError:
                await interaction.response.send_message("You took too long to respond!",ephemeral=True)
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
    @ui.button(label="Color", style=discord.ButtonStyle.blurple)
    async def button_callback3(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.response.send_message("Please enter the color of the embed",ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                try:
                    await msg.delete(delay=0.1)
                    self.embed.color = int(msg.content, 16)
                    await interaction.message.edit(embed=self.embed)
                except ValueError:
                    await interaction.channel.send("Please enter a valid hex code")
            except asyncio.TimeoutError:
                await interaction.response.send_message("You took too long to respond!",ephemeral=True)
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
    @ui.button(label="Image", style=discord.ButtonStyle.grey)
    async def button_callback4(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.response.send_message("Please enter the image url of the embed",ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                self.embed.set_image(url=msg.content)
                await interaction.message.edit(embed=self.embed)
                await msg.delete(delay=0.1)
                
            except asyncio.TimeoutError:
                await interaction.response.send_message("You took too long to respond!",ephemeral=True)
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
    @ui.button(label="Thumbnail", style=discord.ButtonStyle.grey)
    async def button_callback5(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.response.send_message("Please enter the thumbnail url of the embed",ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                self.embed.set_thumbnail(url=msg.content)
                await interaction.message.edit(embed=self.embed)
                await msg.delete(delay=0.1)
                
            except asyncio.TimeoutError:
                await interaction.response.send_message("You took too long to respond!",ephemeral=True)
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
    @ui.button(label="Edit Fields",style=discord.ButtonStyle.blurple)
    async def button_callback7(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.message.delete()
            await interaction.response.send_message(view=fieldss_view(self.bot,self.userid,self.guildid,self.embed))
    @ui.button(label="Json",style=discord.ButtonStyle.grey)
    async def button_callback8(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.response.send_message("Please enter the Json in the current channel",ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                if msg.content.startswith("{") and msg.content.endswith("}") and check(msg):
                    try:
                        data = json.loads(msg.content)
                        self.embed = discord.Embed.from_dict(data)
                        await interaction.delete_original_response()
                        await interaction.message.delete()
                        await msg.delete()
                        await interaction.channel.send(embed=self.embed,view=EmbedBuilder(self.bot,interaction.user.id,interaction.guild.id,self.embed))
                    except json.JSONDecodeError:
                        await interaction.channel.send("try again!  Please enter a valid JSON")
            except asyncio.TimeoutError:
                await interaction.channel.send("You took too long to respond! Please try again")
        else:
            await interaction.channel.send("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)
    @discord.ui.button(label="Save",style=discord.ButtonStyle.green)
    async def button_callback(self, interaction, button):
            #convert the self.embed into Json
            embed_json = self.embed.to_dict()
            embed_json = json.dumps(embed_json)
            cursor.execute("UPDATE welcome SET message = ? WHERE server_id = ?",(embed_json,self.guildid))
            welcome.commit()
            await interaction.message.delete()
            m=we(interaction.guild.id,"Welcome message smart configuration ",footer_icon,interaction.user.name, interaction.user.avatar.url)
            m.set_footer(text=f"Welcome message has been changed")
            await interaction.response.send_message(embed=m,view=wb1(self.bot,self.userid))
    @ui.button(label="Cancel",style=discord.ButtonStyle.red)
    async def button_callback6(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.message.delete()
        else:
            await interaction.response.send_message("You are not the author of this!\nplease consider calling your own command via **!welcome** or **/welcome**",ephemeral=True)

# Dropdown for selection of fields :)
class field_select(ui.Select):
    def __init__(self,bot,userid,guildid,eembed):
        self.bot= bot
        self.userid=userid
        self.guildid=guildid
        self.embed = eembed
        options = [ discord.SelectOption(label=field.name, value=field.value) for field in self.embed.fields ]
        super().__init__(placeholder="Select a field to edit", options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(FieldModal(self.bot,self.userid,self.guildid,self.embed,self.values[0]))
class fieldss_view(ui.View):
    def __init__(self,bot,userid,guildid,eembed):
        super().__init__()
        self.bot= bot
        self.userid=userid
        self.guildid=guildid
        self.embed = eembed
        self.add_item(field_select(self.bot,self.userid,self.guildid,self.embed))
# View for dm settings.

class dm_button(ui.View):
    def __init__(self,bot,userid,guildid):
        super().__init__()
        self.bot= bot
        self.userid=userid
        self.guildid=guildid
    @ui.button(label="Edit message", style=discord.ButtonStyle.blurple)
    async def button_callback(self, interaction, button):
        if interaction.user.id == self.userid:
            session=aiohttp.ClientSession()
            view=(BaseView(interaction, session,"dm"))
            j=embed("Dm settings","Interact with the buttons below to edit the dm settings",0x90ee90)
            await interaction.response.send_message(embed=j,view=view)
    @ui.button(label="Test", style=discord.ButtonStyle.blurple)
    async def button_callback2(self, interaction, button):
        if interaction.user.id == self.userid:
            await interaction.response.send_message("please select a channel from the channel select below",view=dmchannelselectm(self.bot,self.userid,self.guildid))
    @ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def button_callback3(self, interaction, button):
        #disable the buttons
        for child in self.children:
            child.disabled = True
            
# channel select for dm settings
class droop_down(ui.ChannelSelect):
    def __init__(self, bot,userid,guildid):
        super().__init__(placeholder="Select a channel", min_values=1, max_values=1)
        self.bot = bot
        self.userid = userid
        self.guildid = guildid

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.userid:
            await interaction.response.send_message(f"You selected: {self.values[0].mention}")
            channel=self.values[0].id
            # get the message from the database
            cursor.execute("SELECT message FROM dm WHERE server_id = ?", (interaction.guild.id,))
            messagejson=cursor.fetchone()
            #send the message
            if messagejson is None:
                await interaction.channel.send("Welcome message is not set")
            if messagejson is not None:
                # Get the channel
                x = self.bot.get_channel(channel)
                # Read the json
                messagejson = json.loads(messagejson[0])
                # Convert the json to a discord message
                content=messagejson["content"]
            embeds=messagejson["embeds"]
            eembeds=[]
            for embed in embeds:
                embeds=discord.Embed.from_dict(embed)
                eembeds.append(embeds)
                channel=self.values[0].id
                chanel=self.bot.get_channel(channel)
                
                content=messagejson["content"]
                await chanel.send(content=content,embeds=eembeds)
# channelselectm view
class dmchannelselectm(ui.View):
    def __init__(self, bot,userid,guildid):
        super().__init__()
        self.bot = bot
        self.userid = userid
        self.guildid = guildid
        self.add_item(droop_down(self.bot,self.userid,self.guildid))
