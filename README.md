# Silliana
Silly bot for Hexa Vibes Discord Server, written in Python using the `discord.py` library.

## Local Development
### Prerequisities
The bot is quite simple to set up and doesn't require any database (for now). All you need is to have Python (and PIP, if not included) installed, and have created your own bot account in the Discord Developer Portal.

For the 'Bwaa' response (or probably moderation in the future), you need to have the intent `MESSAGE_CONTENT` enabled, as required by Discord's API.

And for monitoring Twitch streams (to check whether you're live or not), you need to get the credentials by registering an app in Twitch Developers Console.

### Setup
1. For external contributors, fork the repository, then clone it to your local PC.
2. Create a [virtual environment (venv)](https://docs.python.org/3/library/venv.html), optional but recommended to prevent library conflicts.
3. Install the required libraries using this command:
```sh
$ pip install -r requirements.txt

# Or in venv (replace "{venv python path} with your venv python program")
$ {venv python path} -m pip install -r requirements.txt
```
4. Copy the `.env.template` and rename the copy to `.env`.
5. Fill in the required configurations to the `.env` file, such as Token, App ID, Channel ID, etc.
6. Lastly, run the bot via:
```ps1
# Windows
> python silliana.py
```
```sh
# Most Linux distros
$ python3 silliana.py
```

### Contribution
crispy-caesus
SenkoNyan
herrlayre
