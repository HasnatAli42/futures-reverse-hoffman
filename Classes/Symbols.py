import time

import pandas as pd
import requests

from BinanceFuturesPy.futurespy import Client
from Config.Settings import LIMIT, Dollars, Leverage

symbols = ["BTCBUSD", "ETHBUSD", "BNBBUSD", "ADABUSD", "XRPBUSD", "DOGEBUSD", "SOLBUSD", "FTTBUSD",
           "AVAXBUSD", "NEARBUSD", "GMTBUSD", "APEBUSD", "GALBUSD", "FTMBUSD", "DODOBUSD", "ANCBUSD",
           "GALABUSD", "TRXBUSD", "1000LUNCBUSD", "LUNA2BUSD", "DOTBUSD", "TLMBUSD", "ICPBUSD",
           "WAVESBUSD", "LINKBUSD", "SANDBUSD", "LTCBUSD", "MATICBUSD", "CVXBUSD", "FILBUSD",
           "1000SHIBBUSD", "LEVERBUSD", "ETCBUSD", "LDOBUSD"]
decimal_point_qty = [3, 3, 2, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 2, 0, 1,
                     1, 0, 0, 1, 1]
decimal_point_price = [1, 2, 2, 4, 4, 5, 2, 2, 3, 3, 4, 3, 3, 4, 4, 4, 6, 6, 4, 4, 3, 5, 3, 3, 3, 3, 2, 4,
                       3, 3, 6, 6, 3, 3]

upper_sharpness = [1.001, 1.0015, 1.002, 1.0025, 1.003, 1.004, 1.005]
lower_sharpness = [0.999, 0.9985, 0.998, 0.9975, 0.997, 0.996, 0.995]
timeframe = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1D"]


class Symbols:

    def __init__(self, current_index_symbol, current_index_time_frame):
        self.symbols = symbols
        self.decimal_point_qty = decimal_point_qty
        self.decimal_point_price = decimal_point_price
        self.upper_sharpness = [1.002, 1.0025, 1.003, 1.004, 1.005]
        self.lower_sharpness = [0.998, 0.9975, 0.997, 0.996, 0.995]
        self.timeframe = ["15m", "30m", "1h", "2h", "4h"]
        self.moved_symbols_list = []
        self.current_index = current_index_symbol
        self.current_symbol = self.symbols[self.current_index]
        self.current_decimal_point_qty = self.decimal_point_qty[self.current_index]
        self.current_decimal_point_price = self.decimal_point_price[self.current_index]
        self.current_QNTY = self.dollars_to_cryto_quantiy(Dollars)
        self.api_key = "FBenBPte1P8oxxul5WmL5oxluUd3GGH83RnmGU1v40wxqw1dPh8qAREvKG7nWzad"
        self.secret_key = "M2xd43ai6fLTgwxmEtGT6PAmnMw6wcG61qq7ft1xLlCclvTafZHU63t1dePlvzIE"
        self.current_symbol_price = self.get_price()
        self.current_index_timeframe = current_index_time_frame
        self.current_timeframe = self.timeframe[self.current_index_timeframe]
        self.current_upper_sharpness = self.upper_sharpness[self.current_index_timeframe]
        self.current_lower_sharpness = self.lower_sharpness[self.current_index_timeframe]

    def verify_data(self):
        if len(self.symbols) == len(self.symbols) == len(self.symbols):
            print("Verified with Length = ", len(self.symbols))
        else:
            print("UnVerified")

    def increment(self):
        if self.current_index == len(self.symbols) - 1:
            self.current_index = 0
        else:
            self.current_index += 1
        self.current_symbol = self.symbols[self.current_index]
        self.current_decimal_point_qty = self.decimal_point_qty[self.current_index]
        self.current_decimal_point_price = self.decimal_point_price[self.current_index]
        self.current_QNTY = self.dollars_to_cryto_quantiy(Dollars)

    def move_symbols(self):
        pop_symbol = self.symbols.pop(self.current_index)
        pop_point_qty = self.decimal_point_qty.pop(self.current_index)
        pop_point_price = self.decimal_point_price.pop(self.current_index)
        self.moved_symbols_list.append(pop_symbol)
        if self.current_index == len(self.symbols):
            self.current_index = 0
        self.current_symbol = self.symbols[self.current_index]
        self.current_decimal_point_qty = self.decimal_point_qty[self.current_index]
        self.current_decimal_point_price = self.decimal_point_price[self.current_index]
        self.current_QNTY = self.dollars_to_cryto_quantiy(Dollars)

    def reset_increment_to_specific_symbol(self, symbol):
        self.symbols = ["BTCBUSD", "ETHBUSD", "BNBBUSD", "ADABUSD", "XRPBUSD", "DOGEBUSD", "SOLBUSD", "FTTBUSD",
                        "AVAXBUSD", "NEARBUSD", "GMTBUSD", "APEBUSD", "GALBUSD", "FTMBUSD", "DODOBUSD", "ANCBUSD",
                        "GALABUSD", "TRXBUSD", "1000LUNCBUSD", "LUNA2BUSD", "DOTBUSD", "TLMBUSD", "ICPBUSD",
                        "WAVESBUSD", "LINKBUSD", "SANDBUSD", "LTCBUSD", "MATICBUSD", "CVXBUSD", "FILBUSD",
                        "1000SHIBBUSD", "LEVERBUSD", "ETCBUSD", "LDOBUSD"]
        self.decimal_point_price = [1, 2, 2, 4, 4, 5, 2, 2, 3, 3, 4, 3, 3, 4, 4, 4, 6, 6, 4, 4, 3, 5, 3, 3, 3, 3, 2, 4,
                                    3, 3, 6, 6, 3, 3]
        self.decimal_point_qty = [3, 3, 2, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 2, 0, 1,
                                  1, 0, 0, 1, 1]
        self.current_index = self.symbols.index(symbol)
        self.current_symbol = self.symbols[self.current_index]
        self.current_decimal_point_qty = self.decimal_point_qty[self.current_index]
        self.current_decimal_point_price = self.decimal_point_price[self.current_index]
        self.current_QNTY = abs(self.position_quantity_any_direction(SYMBOL=symbol, client=self.client()))

    def increment_harmonics(self):
        if self.current_index == len(self.symbols) - 1:
            self.current_index = 0
            if self.current_index_timeframe == len(self.timeframe) - 1:
                self.current_index_timeframe = 0
            else:
                self.current_index_timeframe += 1
        else:
            self.current_index += 1
        self.current_symbol = self.symbols[self.current_index]
        self.current_decimal_point_qty = self.decimal_point_qty[self.current_index]
        self.current_decimal_point_price = self.decimal_point_price[self.current_index]
        self.current_QNTY = self.dollars_to_cryto_quantiy(Dollars)
        self.current_timeframe = self.timeframe[self.current_index_timeframe]
        self.current_upper_sharpness = self.upper_sharpness[self.current_index_timeframe]
        self.current_lower_sharpness = self.lower_sharpness[self.current_index_timeframe]

    def client(self):
        client = Client(api_key=self.api_key, sec_key=self.secret_key, testnet=False, symbol=self.current_symbol,
                        recv_window=30000)
        client.change_leverage(Leverage)
        return client

    def cancel_all_orders(self, fake_argument1, fake_argument2, fake_argument3):
        while self.moved_symbols_list:
            client = Client(api_key=self.api_key, sec_key=self.secret_key, testnet=False,
                            symbol=self.moved_symbols_list[0],
                            recv_window=30000)
            if self.position_quantity_any_direction(SYMBOL=self.moved_symbols_list[0], client=client) == 0:
                order = client.cancel_all_open_orders(self.moved_symbols_list[0])
                if order["code"] == 200:
                    self.moved_symbols_list.remove(self.moved_symbols_list[0])
            else:
                self.moved_symbols_list.remove(self.moved_symbols_list[0])

    def position_quantity_any_direction(self, SYMBOL, client: Client):
        posInfo = client.position_info()
        for counter in posInfo:
            if counter["symbol"] == SYMBOL:
                quantity = float(counter["positionAmt"])
                return quantity

    def get_price(self):
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={self.current_symbol}"
        except Exception as e:
            time.sleep(180)
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={self.current_symbol}"
        res = requests.get(url)
        self.current_symbol_price = float(res.json()['price'])
        return self.current_symbol_price

    def get_price_spot(self, symbol):
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        except Exception as e:
            time.sleep(180)
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url)
        self.current_symbol_price = float(res.json()['price'])
        return self.current_symbol_price

    def dollars_to_cryto_quantiy(self, quantity):
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={self.current_symbol}"
        except Exception as e:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={self.current_symbol}"
        res = requests.get(url)
        return round((quantity / float(res.json()['price'])), self.current_decimal_point_qty)

    def get_data(self, timeframe):
        url = "https://fapi.binance.com/fapi/v1/klines?symbol={}&interval={}&limit={}".format(self.current_symbol,
                                                                                              timeframe,
                                                                                              LIMIT)
        res = requests.get(url)
        closed_data = []
        for each in res.json():
            closed_data.append(each)
        data = pd.DataFrame(data=closed_data).iloc[:, 1: 5]
        data.columns = ["open", "high", "low", "close"]
        data["open"] = pd.to_numeric(data["open"])
        data["high"] = pd.to_numeric(data["high"])
        data["low"] = pd.to_numeric(data["low"])
        data["close"] = pd.to_numeric(data["close"])
        return data["open"], data["high"], data["low"], data["close"]

    def print(self):
        print(self.current_index, ".", self.current_symbol, " : ", self.current_symbol_price)

    def print_current_status(self):
        print(
            "********************* Finding Harmonics For " + self.current_symbol + " at TimeFrame = " + self.current_timeframe + " ******************************")
