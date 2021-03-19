# Crypto ATH Telegram Bot

This bot uses the CoinGecko API and analyses the top 1500 cryptocurrencies every 30 seconds looking for new all time highs.

## Requirements

- **Python 3**
- **Pipenv**
- Once you have Pipenv, use **pipenv install** in the directory you have cloned the bot to in order to install the rest of the dependencies.

## How to set up

- Obtain a Telegram API key from the @botfather telegram account.
-  Assign this API key to the **'API_KEY'** variable in constants.py.
-  Assign the chat id of the telgram chat in which you want this bot to function to the **'tg_chat_id'** variable in botfunctions.py.
-  Can run locally or be run in the cloud for continuous all time high monitoring.
