from Classes.TradingBot import TradingBot
import time
from Config.Settings import TIME_SLEEP


def allow_thread(t_obj: TradingBot):
    time.sleep(TIME_SLEEP * 4)
    t_obj.isThreadAllowed = True
