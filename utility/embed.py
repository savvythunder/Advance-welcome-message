import discord
import sqlite3
welcoe = sqlite3.connect('db/welcome.sql')
w = welcoe.cursor()
def embed(title, description, color):
    """Create a Discord embed with a title, description, and color."""
    return discord.Embed(title=title, description=description, color=color)

def field(embed, name, value, inline):
    """Add a field to a Discord embed."""
    embed.add_field(name=name, value=value, inline=inline)
def we(guild_id,footer,icon,author,author_icon):
        """Embed for welcome function"""
        data=w.execute("SELECT * FROM welcome WHERE server_id = ?", (guild_id,))
        data=data.fetchone()
        m=embed("Welcome configuration","Configure the welcome message by interacting with buttons below",0x90ee90)
        if data[2] is None:
            field(m,"<:channel:1267363232083873833> Channel","Not set",True)
        else:
            field(m,"<:channel:1267363232083873833> Channel",f"<#{data[2]}>",True)
        if data[1] is None:
            field(m,"<:message:1267364231980777483> Message","Not set",True)
        else:
            field(m,"<:message:1267364231980777483> Message",data[1],True)
        if data[3] is None:
            field(m,"<:message:1267367369018445945> On-Join role","Not set",True)
        else:
            field(m,"<:message:1267367369018445945> On-Join role",f" <@&{data[3]}>",True)

    
        if footer is not None:
            m.set_footer(text=footer, icon_url=icon)
        if author is not None:
            m.set_author(name=author, icon_url=author_icon)
        return m
    
