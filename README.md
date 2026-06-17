# Timetable Parser Telegram Bot

Timetable Parser Telegram Bot is an asynchronous Telegram bot for working with transport schedules, train timetables and weather information.

The bot uses interactive menus, parses external web sources and helps users quickly get relevant timetable information directly in Telegram.

## Stack

- Python
- aiogram
- asyncio
- requests
- BeautifulSoup
- Telegram Bot API

## Features

- Telegram bot interface
- Interactive inline menu
- Transport timetable output
- Nearest bus calculation
- Separate logic for weekdays and weekends
- Train timetable parsing from external web sources
- Weather information parsing
- Callback query handling
- Message editing instead of sending duplicate messages
- Basic error handling for Telegram API responses

## Project structure

```text
new_router_bot.py
db_for_udacha_v3.py
requirements.txt
README.md
.env.example
.gitignore
```

## Requirements

- Python 3.10+
- pip
- virtualenv
- Telegram bot token from BotFather
- Internet connection

## Environment variables

Create a `.env` file in the root folder of the project.

The `.env` file should contain:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

The real Telegram bot token must be stored only in the local `.env` file.

Do not publish real tokens, API keys or private IDs on GitHub.

## How to run

Clone the repository:

```bash
git clone https://github.com/GriphinTerner/timetable_parser_bot.git
cd timetable_parser_bot
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment on macOS / Linux:

```bash
source venv/bin/activate
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Upgrade pip:

```bash
pip install --upgrade pip
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```bash
touch .env
```

Add your Telegram bot token to `.env`:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

Run the bot:

```bash
python bot.py
```

## Files description

### `bot.py`

Main bot file.

It contains Telegram bot handlers, interactive menu logic, callback query processing and user interaction scenarios.

### `db_v3.py`

Data and timetable logic file.

It contains schedule data, timetable processing functions and helper logic used by the bot.

### `requirements.txt`

Project dependencies.

Install them with:

```bash
pip install -r requirements.txt
```

### `.env.example`

Example environment file.

It should not contain real private tokens.

## Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is activated.

Then reinstall dependencies:

```bash
pip install -r requirements.txt
```

### Bot does not start

Check that the `.env` file exists and contains a valid Telegram bot token:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

### Telegram token error

Create a new bot token through BotFather and replace the value in `.env`.

### Bot starts, but does not respond

Possible reasons:

- Invalid bot token
- Bot is already running in another process
- Internet connection is unstable
- Telegram API is temporarily unavailable

Restart the bot:

```bash
python bot.py
```

## Recommended `.gitignore`

```gitignore
.env
.env.local
venv/
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.idea/
.vscode/
.DS_Store
*.log
```

## Recommended GitHub repository description

Asynchronous Telegram bot for transport schedules, train timetable parsing and weather information.

## Recommended GitHub topics

```text
python
aiogram
telegram-bot
asyncio
parser
beautifulsoup
transport-schedule
timetable
weather
```

## License

This project is intended for educational and portfolio purposes.
