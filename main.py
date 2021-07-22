import discord
import json
import random
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

client = commands.Bot(command_prefix = '.')
token = os.getenv('DISCORD_TOKEN')
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('.help for bot help'))
    print('Bot is ready.')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Sorry, wrong command')

@client.command(pass_content=True, aliases=['h'])
async def help(ctx):
    test_e = discord.Embed(colour=discord.Colour.blurple())
    test_e.set_author(name='Bot prefix = . (dot)')
    test_e.add_field(name = 'help/h', value=f'Help command', inline=False)
    test_e.add_field(name = 'start/st', value=f'Start the quiz \n[start<space>name1<space>name2...]', inline=False)
    test_e.add_field(name = 'point/p', value=f'Increase quiz points \n[.p<space>point1<space>point2...]', inline=False)
    test_e.add_field(name = 'top/t', value=f'Show the current score, sorted from top score', inline=False)
    test_e.add_field(name = 'score/s', value=f'Show the current score', inline=False)
    test_e.add_field(name = 'reset/r', value=f'Reset the points', inline=False)
    test_e.add_field(name='end/e', value=f'End the current game and show the results \n[.end<space>quiz title]', inline=False)
    await ctx.send(embed=test_e)


@client.command(aliases=['r'])
async def reset(ctx):
    with open('score.json', 'w') as f:
        f.write('{}')
    await ctx.send(f'Points has been reset!')


@client.command(aliases=['st'])
async def start(ctx, *name: str):

    nplayer = len(name)
    scores = {}

    for person in name:
            scores.update({person: 0})

    with open('score.json', 'r') as f:
        data = json.load(f)

    for player, poin in scores.items():
        data[player] = poin

    with open('score.json', 'w') as f:
        json.dump(data, f, indent=4)

    await ctx.send(f'There are {nplayer} (more) player(s) in this quiz')
    await score(ctx)



@client.command(aliases=['s'])
async def score(ctx):
    with open('score.json', 'r') as f:
        data = json.load(f)
        leaderboard = []
        for player, point in data.items():
            leaderboard.append(f'{player} has {point} score')

    s = '\n'.join(leaderboard)
    embed = discord.Embed(title='Player Scores', colour=discord.Color.orange())
    embed.add_field(name='Player name :', value=s)
    await ctx.send(embed=embed)


@client.command(aliases=['t'])
async def top(ctx):
    with open('score.json', 'r') as f:
        data = json.load(f)
        data_sorted = sorted(data.items(), key=lambda x: x[1], reverse=True)
        leaderboard = []
        for i in data_sorted:
            leaderboard.append(f'{i[0]} has {i[1]} score')

    s = '\n'.join(leaderboard[1:])
    embed = discord.Embed(title='Player Scores', colour=discord.Color.orange())
    embed.add_field(name=f':trophy:{leaderboard[0]}', value=s, inline=False)
    await ctx.send(embed=embed)


@client.command(aliases = ['poin', 'point'])
async def p(ctx, *poinN: float):
    with open('score.json', 'r') as f:
        data = json.load(f)

    i = 0
    for player, point in data.items():
        result = point+poinN[i]
        data.update({player: result})
        i = i + 1

    with open('score.json', 'w') as f:
        json.dump(data, f, indent=4)

    await score(ctx)



@client.command(aliases=['e'])
async def end(ctx, *, quiz_name):
    with open('score.json', 'r') as f:
        data = json.load(f)
        data_sorted = sorted(data.items(), key=lambda x: x[1], reverse=True)
        if data_sorted[0][1] == data_sorted[1][1]:
            winner = f'**{data_sorted[0][0]}** and **{data_sorted[1][0]}**'

            leaderboard = []
            for i in data_sorted:
                leaderboard.append(f'{i[0]} has {i[1]} score')

            s = '\n'.join(leaderboard[2:])
        else:
            winner = f'**{data_sorted[0][0]}**'

            leaderboard = []
            for i in data_sorted:
                leaderboard.append(f'{i[0]} has {i[1]} score')

            s = '\n'.join(leaderboard[1:])
    
        
    if data_sorted[0][1] == data_sorted[1][1]:
        embed = discord.Embed(title=f"We have a double Winner!! \nrejoice both :trophy:{winner}:trophy:",
                              colour=discord.Color.red())
        embed.add_field(name='Quiz Name : ', value=quiz_name)
        embed.add_field(name=f'Score : ', value=f'**{leaderboard[0]}**\n**{leaderboard[1]}**\n{s}', inline=False)

    else:
        embed = discord.Embed(title=f"Congrats :trophy:{winner}:trophy: you're the Winner!!",
                              colour=discord.Color.red())
        embed.add_field(name='Quiz Name : ', value=quiz_name)
        embed.add_field(name=f'Score : ', value=f'**{leaderboard[0]}**\n{s}', inline=False)

    embed.set_footer(text=f"This message will be pinned automatically.")

    try:
        with open('winlibrary.json', 'r') as f:
            winlibrary = json.load(f)
            print(winlibrary)
            embed.set_image(url=random.choice(winlibrary))
    except:
        print ('fail to read winlibrary')

    msg = await ctx.send(embed=embed)
    await msg.pin()
    await reset(ctx)

@start.error
async def start_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Do you mean start<space>player-name?")

@score.error
async def score_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(f"Sorry, there's no quiz yet")


@top.error
async def top_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(f"Sorry, there's no quiz yet")


@p.error
async def p_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(f"Oops, you forget to insert all points")

@end.error
async def end_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Don't forget to insert the quiz title!")


client.run(token)
