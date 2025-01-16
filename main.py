import discord
from discord.ext import commands
import asyncio
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["BOT_TOKEN"]
WHITELISTED_IDS = config["WHITELISTED_IDS"]

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='+', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.command()
async def dmall(ctx, *, message):
    if ctx.author.id in WHITELISTED_IDS:
        members_to_message = [member for member in ctx.guild.members if not member.bot]
        total_members = len(members_to_message)
        batch_size = 10
        delay_between_batches = 10
        delay_between_messages = 1

        status_message = await ctx.send(f"Starting DM process... 0/{total_members} messages sent")
        sent_count = 0

        for i in range(0, total_members, batch_size):
            batch = members_to_message[i:i+batch_size]

            for member in batch:
                try:
                    await member.send(message)
                    sent_count += 1
                    await status_message.edit(content=f"DMing in progress... {sent_count}/{total_members} messages sent")
                    await asyncio.sleep(delay_between_messages)
                except discord.errors.Forbidden:
                    await ctx.send(f"Unable to send a message to {member.name} (DMs disabled or blocked)!")
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        print("Rate limit reached, waiting... (Error 429)")
                        retry_after = e.response.get("Retry-After", 5)
                        await asyncio.sleep(retry_after)
                    else:
                        await ctx.send(f"HTTP error while sending a message to {member.name}: {e}")
                except Exception as e:
                    await ctx.send(f"Error while sending a message to {member.name}: {e}")

            if i + batch_size < total_members:
                print(f"Waiting {delay_between_batches} seconds before sending the next batch...")
                await asyncio.sleep(delay_between_batches)

        await status_message.edit(content=f"DM process completed! {sent_count}/{total_members} messages sent")
    else:
        await ctx.send("You are not authorized to use this command.")

@bot.command(name="customhelp")
async def help_command(ctx):
    help_message = (
        "+dmall [message]: Sends a private message to all members of the server **(Whitelisted users only)**\n"
        "+customhelp: Displays the list of available commands"
    )
    await ctx.send(help_message)

bot.run(BOT_TOKEN)
