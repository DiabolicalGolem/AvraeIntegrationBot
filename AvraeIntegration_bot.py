# AvraeIntegration_bot.py
import os, sys, logging
import discord, asyncio
from dotenv import load_dotenv
from discord.ext import commands

"""
Initialize
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log")
    ]
)

load_dotenv(override=True)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(intents=discord.Intents.all(),command_prefix="!",help_command=None)

"""
Bot Events
"""
@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    logging.info("\n\n")
    logging.info(
        f"[93m\"{bot.user}\"[32m is connected to the following guild:\n"
        f"    [93m\"{guild.name}\"[32m (id: [93m{guild.id}[32m)[0m"
    )

    await bot.change_presence(activity=discord.Game(name="D&D | !integrationhelp"))
    logging.info("[32mChanged bot presence.[0m")
    logging.info("[32mReady.[0m")

@bot.event
async def on_member_join(member):
    logging.info(f"[93m{member.display_name}[0m has joined.[0m")

    player_role = discord.utils.get(member.guild.roles, name="Player")
    await member.add_roles(player_role)
    logging.info("[32mMade them \"Player\" role.[0m")

@bot.event
async def on_command_error(ctx, error):
    # Ignore unknown commands
    if isinstance(error, commands.CommandNotFound):
        return

"""
Bot Commands
"""
@bot.command(name="integrationhelp",description="Is the help command for the Avrae Integration bot.")
async def integration_help(ctx):
    logging.info(f"[93m{ctx.author}[0m issued: [36mintegrationhelp[0m")

    await ctx.message.delete()  # Clear the issuing command
    logging.info("[32mDeleted issuing command.[0m")
    embed = discord.Embed(title="Avrae Integration Help", description=(
        "This bot is intended to help steamline the use of the Avrae D&D bot. It is maintained and managed by DiabolicalGolem, so it may be down sometimes.\n"
        "Below is a list of commands that should help keep D&D over Discord an easy and enjoyable experience.\n\n"
        "**Core Commands:**\n"
        "**claimdm** - Claims the role of \"DM\" from the active DM.\n"
        "**dnd** - Starts a thread intended for using the Avrae D&D bot. To use, type `!dnd` or `!dnd [title]`.\n"
        "**dndend** - Deletes the `dnd` thread.\n"
        "**dndren** - Renames the `dnd` thread. Use it like: `!dndren [new_name]`\n"
        "**integrationhelp** - The help command for the Avrae Integration bot.\n"
        "**undm** - Returns the current DM to the role of \"Player\"."
    ))
    await ctx.send(embed=embed)
    logging.info("[32mSent the embed.[0m")

@bot.command(name="claimdm",description="Claims the role of \"DM\" from the active DM.")
async def claim_dm(ctx):
    logging.info(f"[93m{ctx.author} [0missued: [36mclaim_dm[0m")

    await ctx.message.delete()  # Clear the issuing command
    logging.info("[32mDeleted issuing command.[0m")

    # Establish objects
    dm_role = discord.utils.get(ctx.guild.roles, name="DM")
    player_role = discord.utils.get(ctx.guild.roles, name="Player")
    
    claiming_user = ctx.author
    current_dm = discord.utils.get(ctx.guild.members, roles=[dm_role])
    logging.info(
        "[32mGrabbed role info:\n"
        f"    [0mclaiming_user: [93m{claiming_user}"
        f"    [0mcurrent_dm: [93m{current_dm}[0m"
    )
    
    # Check DM status
    if dm_role in claiming_user.roles:
        message = await ctx.channel.send("You already have the \"DM\" role.")
        logging.error(
            "[31mAborted: claim_dm;\n"
            f"    [93m{ctx.author} [31malready is DM.[0m"
        )
        async with ctx.typing():
            await asyncio.sleep(4)
            await message.delete()
        return
    
    # Make the switch
    if current_dm:
        await current_dm.remove_roles(dm_role)
        logging.info("[32mRemoved current_dm \"DM\" role.[0m")
        await current_dm.add_roles(player_role)
        logging.info("[32mGave current_dm \"Player\" role.[0m")

    await claiming_user.remove_roles(player_role)
    logging.info("[32mRemoved claiming_user \"Player\" role.[0m")
    await claiming_user.add_roles(dm_role)
    logging.info("[32mGave claiming_user \"DM\" role.[0m")

    message = await ctx.send("You are now the DM.")
    async with ctx.typing():
        await asyncio.sleep(4)
        await message.delete()

@bot.command(name="dnd",description="Starts a thread intended for D&D. Helps keep the server tidy.")
async def dnd_thread(ctx,*args):
    logging.info(f"[93m{ctx.author} [0missued: [36mdnd[0m")

    await ctx.message.delete()  # Clear the issuing command
    logging.info("[32mDeleted issuing command.[0m")
    
    # Find author name
    name = ctx.author.nick
    if not name:
        name = ctx.author.display_name
    logging.info(
        "[32mGrabbed author's name:\n"
        f"    [93m{name}[0m"
    )

    # Establish channel path
    channel = ctx.channel
    if isinstance(ctx.channel, discord.Thread):
        history = [msg async for msg in ctx.channel.history(limit=1,oldest_first=True)]
        channel_id = history[0].reference.channel_id
        channel = bot.get_channel(channel_id)
    logging.info(
        "[32mFound channel path:\n"
        f"    [93m{channel}[0m"
    )

    # Header preparation
    if not args:
        title = f"{str(name)}'s Thread:"
        if name[-1] == "s":
            title = f"{str(name)}' Thread:"
    else:
        title = " ".join(args)
    
    message = await channel.send(title)
    logging.info(
        "[32mSent anchoring message:\n"
        f"    [93m{title}[0m"
    )
    thread = await message.create_thread(name=title)
    logging.info(
        "[32mSet thread title:\n"
        f"    [93m{title}[0m"
    )

    # Welcome text
    await thread.send(
        f"Hi {name}!\n"
        "Use `!help` to see how to use the D&D bot, Avrae.\n"
        "`!integrationhelp` shows the Avrae Integration bot help.\n"
        "You can use `!dndend` to delete this thread."
    )
    logging.info("[32mSent welcome text.[0m")

@bot.command(name="dndend", description="Deletes the thread.")
async def dndend_thread(ctx):
    logging.info(f"[93m{ctx.author} [0missued: [36mdndend[0m")

    await ctx.message.delete()  # Clear the issuing command
    logging.info("[32mDeleted issuing command.[0m")

    # Find and delete active channel
    if isinstance(ctx.channel, discord.Thread):
        history = [msg async for msg in ctx.channel.history(limit=1,oldest_first=True)]
        channel_id = history[0].reference.channel_id
        message_id = history[0].reference.message_id

        channel = bot.get_channel(channel_id)
        reference_message = await channel.fetch_message(message_id)
        logging.info(
            "[32mGrabbed anchor message source:\n"
            f"    [0mchannel_id:[93m{channel_id}[0m, mmessage_id:{message_id}[0m"
        )

        await ctx.channel.delete()
        logging.info("[32mDeleted thread.[0m")
        await reference_message.delete()    # Delete anchor message
        logging.info("[32mDeleted anchor message.[0m")
    else:
        message = await ctx.send("You can only use `!dndend` in a thread.")
        logging.error(
            "[31mAborted: dndend;\n"
            f"    [93m{ctx.author} [31missued command outside thread.[0m"
        )
        async with ctx.typing():
            await asyncio.sleep(4)
            await message.delete()
            logging.info("[31mServed failure message.[0m")

@bot.command(name="dndren",description="Renames the `dnd` thread.")
async def dnd_rename(ctx,*args):
    logging.info(f"[93m{ctx.author} [0missued: [36mdndren[0m")
    
    await ctx.message.delete()  # Clear the issuing command
    logging.info("[32mDeleted issuing command.[0m")


    if not isinstance(ctx.channel, discord.Thread):
        message = await ctx.send("You can only use `!dndren` in a thread.")
        async with ctx.typing():
            await asyncio.sleep(4)
            await message.delete()
            logging.info("[31mServed failure message.[0m")
        return

    # Error handling
    if not args:
        message = await ctx.send("Please provide a name for the Thread.")
        logging.error(
            "[31mAborted: dndren;\n"
            f"    [93m{ctx.author} [31missued command without new_name.[0m"
        )
        async with ctx.typing():
            await asyncio.sleep(4)
            await message.delete()
            logging.info("[31mServed failure message.[0m")
        return
    
    # Rename the thread
    new_name = " ".join(args)
    logging.info(
        "[32mJoined new_name:\n"
        f"    [0mnew_name: \"[93m{new_name}[0m\""
    )

    await ctx.channel.edit(name=new_name)
    logging.info("[32mChanged thread name to new_name[0m")
    
@bot.command(name="undm",description="Returns the current DM to the role of \"Player\".")
async def unclaim_dm(ctx):
    logging.info(f"[93m{ctx.author} [0missued: [36mun_dm[0m")

    await ctx.message.delete()  # Clear the issuing command
    logging.info("[32mDeleted issuing command.[0m")

    # Establish objects
    dm_role = discord.utils.get(ctx.guild.roles, name="DM")
    player_role = discord.utils.get(ctx.guild.roles, name="Player")

    unclaiming_user = ctx.author
    dm_members = [member for member in ctx.guild.members if dm_role in member.roles]
    logging.info(
        "[32mGrabbed role info:\n"
        f"    [0munclaiming_user: [93m{unclaiming_user}"
        f"    [0mdm_members: [93m{dm_members}[0m"
    )
    
    # Check DM status
    unclaim_invalid = True
    if unclaiming_user in dm_members:
        unclaim_invalid = False

    if unclaim_invalid:
        message = await ctx.send("You don't have the \"DM\" role.")
        logging.error(
            "[31mAborted: un_dm;\n"
            f"    [93m{ctx.author} [31mis not DM.[0m"
        )
        async with ctx.typing():
            await asyncio.sleep(4)
            await message.delete()
            logging.info("[31mServed failure message.[0m")
        return
    
    # Make the switch
    await unclaiming_user.remove_roles(dm_role)
    logging.info("[32mRemoved current_dm \"DM\" role.[0m")
    await unclaiming_user.add_roles(player_role)
    logging.info("[32mGave current_dm \"Player\" role.[0m")
    message = await ctx.send("You are no longer the DM.")
    async with ctx.typing():
        await asyncio.sleep(4)
        await message.delete()

bot.run(TOKEN)