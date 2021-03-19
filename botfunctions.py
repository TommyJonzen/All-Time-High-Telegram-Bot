from pycoingecko import CoinGeckoAPI
import time
import constants as keys
import telegram
import logging

# Create and configure logging
log_format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename='cg.log', level=logging.DEBUG, format=log_format)
logger = logging.getLogger()

# CoinGecko API Variable
cg = CoinGeckoAPI()

# TG Bot API setup and chat ID
bot = telegram.Bot(token=keys.API_KEY)
tg_chat_id = ''

# Limit on how long to wait before updating on same coin
time_limit = 300


# Pull initial ATH when the script starts
def start():
    ath_dict = {}
    for i in range(1, 7):
        coins = cg.get_coins_markets(vs_currency='usd', per_page=250, page=i)
        logger.info(f"CG page {i} pulled during start sequence")
        for j in coins:
            ath_dict[j['id']] = [j['ath'], (time.time() - time_limit)]
    return ath_dict


# Pull current price regularly to compare to ATH
def cg_cont_request():
    current_price = {}
    coin_list = []
    for i in range(1, 7):
        coins = cg.get_coins_markets(vs_currency='usd', per_page=250, page=i)
        logger.info(f"CG page {i} pulled during continuous request sequence")
        for j in coins:
            current_price[j['id']] = [j['ath'], time.time()]
            coin_list.append(j)
    return coin_list, current_price


def ath_checker(ath_dict):
    while True:
        # Continuously pull coin data to check for new all time highs
        logger.info('ath_checker - Running Script')
        try:
            all_coin_info, new_ath = cg_cont_request()
        except Exception as e:
            logger.warning(f"cg_cont_request exception occurred: {e}")
            time.sleep(30)
            continue

        for i in new_ath:
            if i in ath_dict:

                # If there is a new all time high
                if new_ath[i][0] > ath_dict[i][0]:

                    # Adjust ATH dict to reflect a New ATH and add time of new ATH
                    time_check = ath_dict[i][1]
                    ath_dict[i] = new_ath[i]

                    # Report new ATH if the coin hasn't been reported on recently
                    if time_check < time.time() - time_limit:
                        update = []
                        # Pull relevant coins dictionary from list of dictionaries to create update about the coin
                        item = next((j for j, item in enumerate(all_coin_info) if item["id"] == i), None)
                        coin = all_coin_info[item]

                        update.append(f"{coin['name']}")
                        update.append("$" + "{:,}".format(coin['current_price']))
                        update.append("{:,}".format(coin['market_cap_rank']))
                        update.append("$" + "{:,}".format(coin['market_cap']))
                        update.append(str(coin['price_change_percentage_24h']) + "%")
                        update.append("$" + "{:,}".format(coin['total_volume']))
                        update.append("$" + "{:,}".format(coin['ath']))

                        # Send message to TG chat with update
                        bot.send_message(chat_id=tg_chat_id, parse_mode='HTML', text=f"<b>{update[0]}</b> " +
                                         "has reached a new all time high!"
                                         + '\n\n' + "<b>New ATH:</b> " + update[6]
                                         + '\n' + "<b>Current Price:</b> " + update[1]
                                         + '\n' + "<b>Market Cap Rank:</b> " + update[2]
                                         + '\n' + "<b>Market Cap:</b> " + update[3]
                                         + '\n' + "<b>24hr Price Change:</b> " + update[4]
                                         + '\n' + "<b>Volume:</b> " + update[5], timeout=60)
                        logger.info(f"Bot coin update message sent: {coin['name']}")

            # Check if new coin has entered top 1500 list & add it to ath_dict to be tracked
            else:
                ath_dict[i] = new_ath[i]
                logger.info(f"Added entry {i}")

        # Check if an entry has fallen off top 1500 and remove if so
        del_list = []
        for j in ath_dict:
            if j not in new_ath:
                del_list.append(j)
        for k in del_list:
            del ath_dict[k]
            logger.info(f"Deleted entry {k}")
        del_list.clear()

        time.sleep(30)
