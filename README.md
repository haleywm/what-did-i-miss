# what-did-i-miss

A Discord Bot that lets you know what happened since you last posted.

## Usage

The setup of the bot is relatively simple. First, you must setup a discord bot (https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token), and then get the private key.

Next, clone this repo and extract it and whatever, and create a file called `config.py`. Copy the file `sample_config.py`, and fill in at least the KEY, as well as the other values if you'd like. `modules/config.py` contains additional configuration options that are used for specific server values.

Next, you must have installed Python 3.8, as well as pip, and gcc. Install the package dependencies with `python -m pip install --update pip && pip install -r requirements.txt`.

Lastly, the application can be run with `python main.py`.

While nothing exists at the moment, the bot startup can be automated with various tools.

The bot requires the current permissions, in order to run:

| Command         | Server Permissions     | Channel Permissions                              |
| :-------------- | :--------------------- | :----------------------------------------------- |
| `.whatdidimiss` | `read_message_history` | `read_messages`, `send-messages`, `attach_files` |
| `.stop`         | `none`                 | `none`                                           |


## Features

This is a bot that generates wordclouds based on messages that have been posted in the server. Users can invoke it using `.whatdidimiss Time: {num}{d, h, m, s} (Default: 6h), This Channel Only: {True/False} (Default: True)`. For example:

- `.whatdidimiss 1d` will generate a wordcloud using text from all messages in that channel in the last day.
- `.whatdidimiss 30m False` will generate a wordcloud using text from all messages on the server (that the bot has access to) in the last 30 minutes.

## Dependencies

- `Python 3.8`
- `pip`

## Planned Features

I'm planning on adding several features depending on the opinions and suggestions of my friends, including potential features such as:

- Recognizing emoticons and adding them to wordclouds
- Parsing markov chains from user input

## Credits

Included wordcloud font packed using the following open source fonts:

- [Noto Emoji](https://www.google.com/get/noto/)
- [Source Code Pro](https://github.com/adobe-fonts/source-code-pro)