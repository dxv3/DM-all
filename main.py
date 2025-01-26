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

@bot.command(name="help")
async def help(ctx):
    help_message = (
        "+dmall [message]: Sends a DM to all members of the server\n"
        "+cancel: Cancels DMing process"
    )
    await ctx.send(help_message)

bot.run(BOT_TOKEN)