# bot.py
import os

import discord
from discord.ext import commands

from dotenv import load_dotenv
from flask import Flask

### START LOAD .ENV
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
GUILD = os.getenv('GUILD_ID')
WELBYE = os.getenv('WELBYE_CHANNEL')
### END LOAD .ENV

### START INIT BOT
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='?', intents=intents)
bot.remove_command('help')
### END INIT BOT

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.event
async def on_ready():
    # Chang
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game('Call of Dragon'))
    print(f'{bot.user} has connected to Discord!')


@bot.event
async def on_member_join(member):
    for guild in bot.guilds:
        if guild.id == GUILD:
            break

    channel = bot.get_channel(int(WELBYE))
    embed = discord.Embed(title=f'Welcome {member.name}!',
                          color=discord.Color.from_rgb(0, 255, 255))

    embed.set_author(name=f'{guild.name}')
    embed.set_thumbnail(url='https://th.bing.com/th/id/R.51e2c44258298f6058049767668c3b10?rik=wz7vzgKNmgsZjA&pid=ImgRaw&r=0' if guild.icon else None)
    embed.set_image(url=member.display_avatar.url)

    await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(int(WELBYE))
    await channel.send('Bye')


### START KICK/BAN
@bot.command(name='kick',
             description='Kick a member if you have permission for that',
             usage='?kick <member> [reason]')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    await member.create_dm()
    await member.kick(reason=reason)
    if reason != None:
        await ctx.send(f'Kicked {member.mention} for {reason}')
        await member.dm_channel.send(f'{guild.name} kicked you for {reason}')
    else:
        await ctx.send(f'Kicked {member.mention}')
        await member.dm_channel.send(f'{guild.name} kicked you')


@kick.error
async def kick_error(ctx, err):
    if isinstance(err, commands.MissingPermissions):
        await ctx.send("You don't have permission to kick members.")


@bot.command(name='ban',
             description='Ban a member if you have permission for that',
             usage='?ban <member> [reason]')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    await member.create_dm()
    await member.ban(reason=reason)
    if reason != None:
        await ctx.send(f'Banned {member.mention} for {reason}')
        await member.dm_channel.send(f'{guild.name} banned you for {reason}')
    else:
        await ctx.send(f'Banned {member.mention}')
        await member.dm_channel.send(f'{guild.name} banned you')


@ban.error
async def ban_error(ctx, err):
    if isinstance(err, commands.MissingPermissions):
        await ctx.send("You don't have permission to kick members.")


### END KICK/BAN


@bot.command(
    name='help',
    description='List all commands or get help for a specific command',
    usage='?help [command]')
async def help(ctx, command_name: str = None):
    if command_name is None:
        # List all commands
        embed = discord.Embed(title='Help',
                              description='List of available commands:',
                              color=discord.Color.from_rgb(255, 114, 118))
        for command in bot.commands:
            embed.add_field(name=f'?{command.name}',
                            value=command.description,
                            inline=False)
        await ctx.send(embed=embed)
    else:
        # Get help for a specific command
        command = bot.get_command(command_name)
        if command is None:
            await ctx.send(f'No command found with the name {command_name}')
        else:
            embed = discord.Embed(title=f"Help for `!{command.name}`",
                                  description=command.description,
                                  color=discord.Color.from_rgb(255, 114, 118))
            embed.add_field(name="Usage",
                            value=f"!{command.name} {command.usage}"
                            if command.usage else f"!{command.name}",
                            inline=False)
            await ctx.send(embed=embed)

# Run Flask server
if __name__ == '__main__':
    from threading import Thread

    def run():
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

    Thread(target=run).start()
    bot.run(TOKEN)