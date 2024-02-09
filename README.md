# HanhMy Discord Bot

## Overview
HanhMy is a Discord bot that streams music from YouTube URLs in voice channels. It uses Python, discord.py for Discord integration, yt_dlp for downloading audio, and is kept alive on servers with a web server script.

## Installation
1. Clone the repository: `git clone https://github.com/nghiant02/HanhMy-discord-bot`
2. Navigate to the bot directory.
3. Install dependencies: `pip install -r requirements.txt`
4. Set up your Discord bot token in a `.env` file.

## Usage
Run the bot with: `python main.py`
Use commands in Discord:
- `!play [URL]` to play music.
- `!pause`, `!resume`, `!stop`, and `!clear_queue` to manage playback.

## Deployment
The bot is designed to be deployed on cloud platforms like Render and monitored with UptimeRobot for consistent online presence.

## Contributing
Fork the repo, make your changes, and create a pull request if you'd like to contribute.

## Contact
Submit issues or reach out for support through the GitHub repository.
