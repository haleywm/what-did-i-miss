# what-did-i-miss

A Discord Bot that lets you know what happened since you last posted.

## Usage

The setup of the bot is relatively simple. First, you must setup a discord bot (https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token), and then get the private key.

Next, clone this repo and extract it and whatever, and create a file called `config.yml` containing `key: {bot-private-key}`. Read `default-config.yml` to get additional configuration options, and place these in your `config.yml` file to overwrite these values. **DO NOT MODIFY defualt-config.yml**.

Next, you must have installed Python 3.8, as well as pip, and gcc. Install the package dependencies with `python -m pip install --update pip && pip install -r requirements.txt`.

Lastly, the application can be run with `python main.py`.

The bot requires the current permissions, in order to run:

| Command         | Server Permissions     | Channel Permissions                              |
| --------------- | ---------------------- | ------------------------------------------------ |
| `.whatdidimiss` | `read_message_history` | `read_messages`, `send-messages`, `attach_files` |


## Features

This is a bot that generates wordclouds based on messages that have been posted in the server. Users can invoke it using `.whatdidimiss Time: {num}{d, m, or y} (Default: 6h), This Channel Only: {True/False} (Default: True)`. For example:

- `.whatdidimiss 1d` will generate a wordcloud using text from all messages in that channel in the last day.
- `.whatdidimiss 30m False` will generate a wordcloud using text from all messages on the server (that the bot has access to) in the last 30 minutes.

## Planned Features

I'm planning on adding several features depending on the opinions and suggestions of my friends, including potential features such as:

- Allowing users to react with a pin icon on messages to vote that the message be pinned.
- ¯\\\_(ツ)\_/¯
