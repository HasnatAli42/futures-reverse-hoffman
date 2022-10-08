from Classes.TradingBot import TradingBot
import time
from Config.Settings import TIME_SLEEP
from datetime import datetime


def allow_thread(t_obj: TradingBot):
    time.sleep(TIME_SLEEP * 4)
    t_obj.isThreadAllowed = True


def print_order_in_progress(current_symbol, currency_price, place_order_price, take_profit, stop_loss, side):
    if side == "buy":
        print("\n--------- Currency ---------")
        print(current_symbol, ":", currency_price)
        print("Take Profit:",
              place_order_price + (place_order_price * take_profit / 100))
        print("Stop Loss:",
              place_order_price - (place_order_price * stop_loss / 100))
        print("\n************** Strategy Result Long In Progress ***********", datetime.now(), "***********")
    elif side == "sell":
        print("\n--------- Currency ---------")
        print(current_symbol, ":", currency_price)
        print("Take Profit:",
              place_order_price - (place_order_price * take_profit / 100))
        print("Stop Loss:",
              place_order_price + (place_order_price * stop_loss / 100))
        print("\n************** Strategy Result Short In Progress ***********", datetime.now(), "***********")

