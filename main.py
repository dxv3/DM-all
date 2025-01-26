import discord
from discord.ext import commands
import asyncio
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["BOT_TOKEN"]
WHITELISTED_IDS = config["WHITELISTED_IDS"]
cancel_event = asyncio.Event()


intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(name="dxv3", url="https://www.twitch.tv/dxv3"))

@bot.command()
async def cancel(ctx):
    if ctx.author.id in WHITELISTED_IDS:
        cancel_event.set()
        await ctx.send("DMing cancelled")
    else:
        await ctx.send(r"you can't use this cmd! :(")

@bot.command()
async def dmall(ctx, *, message):
    if ctx.author.id in WHITELISTED_IDS:
        cancel_event.clear()
        members_to_message = [member for member in ctx.guild.members if not member.bot]
        total_members = len(members_to_message)
        batch_size = 10
        delay_between_batches = 10
        delay_between_messages = 1 # make higher if shit but 1 works for servers under 200 members

        status_message = await ctx.send(f"Started DMing!!! 0/{total_members} messages sent")
        sent_count = 0
        failed = 0

        for i in range(0, total_members, batch_size):
            batch = members_to_message[i:i+batch_size]

            for member in batch:
                if cancel_event.is_set():
                    await status_message.edit(content=f"DMing cancelled, {sent_count}/{total_members} messages sent")
                    return
                try:
                    await member.send(message)
                    sent_count += 1
                    await status_message.edit(content=f"DMing in progress... {sent_count}/{total_members} messages sent, {failed} failed (msgs disabled)")

                    await asyncio.sleep(delay_between_messages)
                except discord.errors.Forbidden:
                    print(f"unable to send a message to {member.name} (DMs disabled or blocked).")
                    failed += 1
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        print("rate limit reached, waiting... (Error 429)")
                        retry_after = e.response.get("Retry-After", 5)
                        delay_between_messages += 1  # increase delay dynamically
                        await asyncio.sleep(retry_after)
                    else:
                        print(f"HTTP error while sending a message to {member.name}: {e}")
                except Exception as e:
                    print(f"error while sending a message to {member.name}: {e}")

            if i + batch_size < total_members:
                print(f"Waiting {delay_between_batches} seconds before sending the next batch...")
                await asyncio.sleep(delay_between_batches)

        await status_message.edit(content=f"DM process completed! {sent_count}/{total_members} messages sent, {failed} failed (msgs disabled)")

    else:
        await ctx.send(r"you can't use this cmd! :(")

@bot.command()
async def dmallembed(ctx):
    if ctx.author.id in WHITELISTED_IDS:
        cancel_event.clear()
        members_to_message = [member for member in ctx.guild.members if not member.bot]
        total_members = len(members_to_message)
        batch_size = 10
        delay_between_batches = 10
        delay_between_messages = 1

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("Enter the **title** of the embed:")
        title_msg = await bot.wait_for('message', check=check)

        await ctx.send("Enter the **description** of the embed:")
        description_msg = await bot.wait_for('message', check=check)

        color_options = {
            "red": 0xFF0000,
            "green": 0x00FF00,
            "blue": 0x0000FF,
            "black": 0x000000,
            "yellow": 0xFFFF00,
            "purple": 0x800080,
            "orange": 0xFFA500,
            "pink": 0xFFC0CB,
            "gray": 0x808080,
        }
        color_list = "\n".join([f"`{name}`" for name in color_options.keys()])
        await ctx.send(
            f"Choose a **colour** from the list below or enter a hex code (e.g., `#ff5733`):\n{color_list}"
        )

        color_msg = await bot.wait_for('message', check=check)
        color_choice = color_msg.content.lower()

        if color_choice in color_options:
            color = color_options[color_choice]
        else:
            try:
                color = int(color_choice.strip('#'), 16)
            except ValueError:
                await ctx.send("Invalid color choice. Defaulting to black.")
                color = 0x000000

        embed = discord.Embed(
            title=title_msg.content,
            description=description_msg.content,
            color=color
        )

        status_message = await ctx.send(f"Started DMing embed!!! 0/{total_members} messages sent")
        sent_count = 0
        failed = 0

        for i in range(0, total_members, batch_size):
            batch = members_to_message[i:i + batch_size]

            for member in batch:
                if cancel_event.is_set():
                    await status_message.edit(content=f"DMing cancelled, {sent_count}/{total_members} messages sent")
                    return
                try:
                    await member.send(embed=embed)
                    sent_count += 1
                    await status_message.edit(content=f"DMing embed in progress... {sent_count}/{total_members} messages sent, {failed} failed (msgs disabled)")
                    await asyncio.sleep(delay_between_messages)
                except discord.errors.Forbidden:
                    print(f"Unable to send embed to {member.name} (DMs disabled or blocked).")
                    failed += 1
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        retry_after = e.response.get("Retry-After", 5)
                        delay_between_messages += 1
                        await asyncio.sleep(retry_after)
                    else:
                        print(f"HTTP error while sending embed to {member.name}: {e}")
                except Exception as e:
                    print(f"Error while sending embed to {member.name}: {e}")

            if i + batch_size < total_members:
                print(f"Waiting {delay_between_batches} seconds before sending the next batch...")
                await asyncio.sleep(delay_between_batches)

        await status_message.edit(content=f"DM embed process completed! {sent_count}/{total_members} messages sent, {failed} failed (msgs disabled)")

    else:
        await ctx.send(r"you can't use this cmd! :(")


@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(
        title="Help Menu",
        description="List of available commands:",
        color=0x00FF00,
    )
    embed.add_field(
        name="+dmall [message]",
        value="Sends a DM to all members of the server.",
        inline=False,
    )
    embed.add_field(
        name="+dmallembed",
        value="Sends an embed DM to all members of the server.",
        inline=False,
    )
    embed.add_field(
        name="+cancel",
        value="Cancels the DMing process if it's in progress.",
        inline=False,
    )

    await ctx.send(embed=embed)

bot.run(BOT_TOKEN)