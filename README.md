# Discord Bot with DM All Command

This Discord bot allows specific whitelisted users to send private messages (DMs) to all non-bot members of a server. The bot's configuration, including the token and whitelist, is managed through a `config.json` file.

---

if you get `No module named 'audioop'` then do 

## Features

- **Whitelist-Based Access:** Only users with their IDs in the whitelist can use the `+dmall` command.
- **Progress Updates:** The bot updates the progress of the DM process in the channel where the command is invoked.
- **Batch Messaging:** Sends messages in batches to avoid hitting Discord rate limits.
- **JSON Configuration:** Stores the bot token and whitelisted user IDs in a separate `config.json` file for easy management.

---

## Setup Instructions

### Prerequisites

1. Python 3.8 or higher
2. `discord.py` library
3. If you get the error message `No module named 'audioop'` then `pip install audioop-lts`

Install the library using pip:
```bash
pip install discord.py

