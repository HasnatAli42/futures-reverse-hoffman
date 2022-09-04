from datetime import datetime
from Config.Settings import Leverage, above_or_below_wick, \
    TIME_PERIOD, LIMIT, trailing_order_check, trailing_order_increase, TIME_SLEEP, above_or_below_wick_stop_loss
import sqlite3 as sl
import requests
import numpy as np
import pandas as pd
import time
from BinanceFuturesPy.futurespy import Client

class TradingBot:

    def __init__(self):
        self.LowestPrice = 1000000
        self.Highest_Price = 0
        self.order_sequence = 1
        self.isOrderInProgress = False
        self.isLongOrderInProgress = False
        self.isShortOrderInProgress = False
        self.isOrderPlaced = False
        self.isLongOrderPlaced = False
        self.isShortOrderPlaced = False
        self.currency_price = None
        self.profit = None
        self.firstRun = True
        self.remaining_quantity = 0
        self.low_price = 0
        self.high_price = 0
        self.place_order_price = 0
        self.trailing_order_price = 0
        self.new_place_order_price = 0
        self.newHoffmanSignalCheck = False
        self.isBreakEvenCalled = False
        self.isThreadAllowed = True
        self.threadCounter = 0
        self.LongHit = "LongHit"
        self.ShortHit = "ShortHit"
        self.take_profit = 1
        self.stop_loss = 0.4
        self.profit_ratio = 1
        self.order1 = ""
        self.order2 = ""
        self.shortCounter = 0
        self.LongCounter = 0
        self.order_executed_for_symbol = ""
        self.wasThreadLong = False
        self.wasThreadShort = False
        self.thread_currency_price = 0
        self.thread_high_price = 0
        self.thread_take_profit = 0
        self.thread_stop_loss = 0
        self.thread_newHoffmanSignalCheck = False
        self.thread_new_place_order_price = 0
        self.thread_place_order_price = 0

    def update_data_set(self, side, SYMBOL, client: Client, QNTY):
        global total_wallet_balance, available_balance
        con = sl.connect('../orders-executed.db')
        account_details = client.account_info()
        assets_details = account_details["assets"]
        for counter in assets_details:
            if counter["asset"] == "BUSD":
                total_wallet_balance = counter["walletBalance"]
                available_balance = counter["availableBalance"]
        sql = f'INSERT INTO FUTURES_{SYMBOL}_HOFFMAN (order_sequence,  Current_eth_price,' \
              'Etherium_quantity,' \
              'Remaining_quantity,LeverageTaken,TotalWalletBalance,AvailableBalance,' \
              'OrderFee,Method_applied,' \
              'Usd_used,HighestPrice,LowestPrice,OrderPrice,TakeProfitPrice,StopLossPrice, Time, Order1, ' \
              'Order2) values(?,?,?,?,?,?,' \
              '?,?,?,?,?,?,?,?,?,' \
              '?,?,?) '
        data = [
            (str(self.order_sequence)), (str(self.currency_price)),
            (str(QNTY)),
            (str(self.remaining_quantity)), (str(Leverage)),
            (str(total_wallet_balance)),
            (str(available_balance)), (str(round(float(self.currency_price * QNTY * 0.023 / 100), 6))), (str(side)),
            (str(round(float(self.currency_price * QNTY), 6))), (str(self.Highest_Price)), (str(self.LowestPrice)),
            (str(self.place_order_price)), (str(float(
                self.place_order_price + (self.place_order_price * self.take_profit / 100)))), (float(
                self.place_order_price - (self.place_order_price * self.stop_loss / 100))), (str(datetime.now())),
            (str(self.order1)), (str(self.order2)),
        ]
        with con:
            con.execute(sql, data)
            con.commit()
        self.Highest_Price = 0
        self.LowestPrice = 1000000
        self.order1 = ""
        self.order2 = ""

    def update_trailing_order(self,SYMBOL,order):
        con = sl.connect('../orders-executed.db')
        sql = f'INSERT INTO FUTURES_{SYMBOL}_HOFFMAN_TRAILING_ORDERS (Symbol,Order2, Time) values(?,?,?) '
        data = [
            (str(SYMBOL)), (str(order)),
            (str(datetime.now())),
        ]
        with con:
            con.execute(sql, data)
            con.commit()


    def write_to_file(self, currentIndex):
        file = open(f'is_order_in_progress.txt', 'w')
        file.write(str(self.isOrderInProgress))
        file.write("\n" + str(self.isLongOrderInProgress))
        file.write("\n" + str(self.isShortOrderInProgress))
        file.write("\n" + str(self.isOrderPlaced))
        file.write("\n" + str(self.isLongOrderPlaced))
        file.write("\n" + str(self.isShortOrderPlaced))
        file.write("\n" + str(self.newHoffmanSignalCheck))
        file.write("\n" + str(self.order_sequence))
        file.write("\n" + str(self.high_price))
        file.write("\n" + str(self.low_price))
        file.write("\n" + str(self.place_order_price))
        file.write("\n" + str(self.take_profit))
        file.write("\n" + str(self.stop_loss))
        file.write("\n" + str(self.trailing_order_price))
        file.write("\n" + str(currentIndex))
        file.close()

    def trailing_stop_loss_order(self, stop_loss_price, SYMBOL, client: Client, Decimal_point_price, QNTY):
        if self.position_quantity_any_direction(SYMBOL, client) > 0:
            self.order2 = client.new_order(symbol=SYMBOL, orderType="STOP_MARKET", quantity=QNTY, side="SELL",
                                           stopPrice=round(stop_loss_price, Decimal_point_price),
                                           reduceOnly=True)
            self.update_trailing_order(SYMBOL=SYMBOL, order=self.order2)
            if str(self.order2).find("code") >= 0:
                if self.order2["code"] == -2021:
                    self.order2 = client.new_order(symbol=SYMBOL, orderType="MARKET", quantity=QNTY, side="SELL")
                    self.LongHit = "LongHit2021"
                    self.update_trailing_order(SYMBOL=SYMBOL, order=self.order2)

        elif self.position_quantity_any_direction(SYMBOL, client) < 0:
            self.order2 = client.new_order(symbol=SYMBOL, orderType="STOP_MARKET", quantity=QNTY, side="BUY",
                                           stopPrice=round(stop_loss_price, Decimal_point_price),
                                           reduceOnly=True)
            self.update_trailing_order(SYMBOL=SYMBOL, order=self.order2)
            if str(self.order2).find("code") >= 0:
                if self.order2["code"] == -2021:
                    self.order2 = client.new_order(symbol=SYMBOL, orderType="MARKET", quantity=QNTY, side="BUY")
                    self.ShortHit = "ShortHit2021"
                    self.update_trailing_order(SYMBOL=SYMBOL, order=self.order2)


    def place_long_order(self, long, SYMBOL, client: Client, Decimal_point_price, QNTY):
        self.order1 = client.new_order(symbol=SYMBOL, orderType="LIMIT", quantity=QNTY, side="BUY",
                                       price=round((long), Decimal_point_price),
                                       reduceOnly=False, timeInForce='GTC')
        self.isOrderPlaced = True
        self.isLongOrderPlaced = True
        self.isShortOrderPlaced = False
        return self.order1

    def cancel_executed_orders(self, SYMBOL, client: Client, QNTY):
        client.cancel_all_open_orders(SYMBOL)
        self.remaining_quantity = self.position_quantity_any_direction(SYMBOL, client)
        if self.remaining_quantity > 0:
            self.order1 = client.new_order(symbol=SYMBOL, orderType="MARKET", quantity=QNTY, side="SELL")
        elif self.remaining_quantity < 0:
            self.order1 = client.new_order(symbol=SYMBOL, orderType="MARKET", quantity=QNTY, side="BUY")

    def place_short_order(self, short, SYMBOL, client: Client, Decimal_point_price, QNTY):
        client.cancel_all_open_orders(SYMBOL)
        self.order1 = client.new_order(symbol=SYMBOL, orderType="LIMIT", quantity=QNTY, side="SELL",
                                       price=round((short), Decimal_point_price),
                                       reduceOnly=False, timeInForce='GTC')
        # self.order2 = client.new_order(symbol=SYMBOL, orderType="STOP_MARKET", quantity=QNTY, side="BUY",
        #                                stopPrice=round(
        #                                    (short + (short * above_or_below_wick * above_or_below_wick_stop_loss /100)),
        #                                    Decimal_point_price),
        #                                reduceOnly=True)

        self.isOrderPlaced = True
        self.isLongOrderPlaced = False
        self.isShortOrderPlaced = True
        return self.order1

    def place_in_progress_order_limits(self,  SYMBOL, client: Client, Decimal_point_price, QNTY):
        if self.position_quantity_any_direction(SYMBOL, client) > 0:
            self.order1 = client.new_order(symbol=SYMBOL, orderType="LIMIT", quantity=QNTY, side="SELL",
                                           price=round((self.place_order_price + (self.place_order_price * self.take_profit /100)), Decimal_point_price),
                                           reduceOnly=False, timeInForce='GTC')
            self.order2 = client.new_order(symbol=SYMBOL, orderType="STOP_MARKET", quantity=QNTY, side="SELL",
                                           stopPrice=round(
                                               (self.place_order_price - (self.place_order_price * self.stop_loss /
                                                                          100)),
                                               Decimal_point_price),
                                           reduceOnly=True)
            if str(self.order2).find("code") >= 0:
                if self.order2["code"] == -2021:
                    self.order2 = client.new_order(symbol=SYMBOL, orderType="MARKET", quantity=QNTY, side="SELL")
                    self.LongHit = "LongHit2021"

        elif self.position_quantity_any_direction(SYMBOL, client) < 0:
            self.order1 = client.new_order(symbol=SYMBOL, orderType="LIMIT", quantity=QNTY, side="BUY",
                                           price=round(
                                               (self.place_order_price - (self.place_order_price * self.take_profit /
                                                                          100)), Decimal_point_price),
                                           reduceOnly=False, timeInForce='GTC')
            self.order2 = client.new_order(symbol=SYMBOL, orderType="STOP_MARKET", quantity=QNTY, side="BUY",
                                           stopPrice=round(
                                               (self.place_order_price + (self.place_order_price * self.stop_loss /
                                                                          100)),
                                               Decimal_point_price),
                                           reduceOnly=True)
            if str(self.order2).find("code") >= 0:
                if self.order2["code"] == -2021:
                    self.order2 = client.new_order(symbol=SYMBOL, orderType="MARKET", quantity=QNTY, side="BUY")
                    self.ShortHit = "ShortHit2021"

    def place_trailing_stop_loss(self,  SYMBOL, client: Client, Decimal_point_price, QNTY):
        if self.position_quantity_any_direction(SYMBOL, client) > 0:
            if self.currency_price >= (self.trailing_order_price + (self.trailing_order_price *(trailing_order_check/100))):
                self.trailing_order_price = (self.trailing_order_price + (self.trailing_order_price * (trailing_order_increase/100)))
                self.trailing_stop_loss_order(self.trailing_order_price, SYMBOL, client, Decimal_point_price, QNTY)
        elif self.position_quantity_any_direction(SYMBOL, client) < 0:
            if self.currency_price <= (self.trailing_order_price - (self.trailing_order_price *(trailing_order_check/100))):
                self.trailing_order_price = (self.trailing_order_price - (self.trailing_order_price * (trailing_order_increase/100)))
                self.trailing_stop_loss_order(self.trailing_order_price, SYMBOL, client, Decimal_point_price, QNTY)

    def calculate_ema(self, prices, days, smoothing=2):
        ema = [sum(prices[:days]) / days]
        for price in prices[days:]:
            ema.append((price * (smoothing / (1 + days))) + ema[-1] * (1 - (smoothing / (1 + days))))
        return ema

    def tr_calculation(self, high, low, close):
        high_low = high - low
        high_close = np.abs(high - np.array(close)[-1])
        low_close = np.abs(low - np.array(close)[-1])
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return np.array(true_range)

    def calcluate_rma(self, rma_data, rmaPeriod):
        alpha = 1 / rmaPeriod
        rma = []
        for i in range(len(rma_data)):
            rma_cal = ((alpha * rma_data[i - 1]) + ((1 - alpha) * rma_data[i]))
            rma.append(rma_cal)
        return rma

    def upper_and_lower_trend_zone_line(self, high, low, close):
        rma_data = self.tr_calculation(high, low, close)
        rma = self.calcluate_rma(rma_data, 35)[-1]
        k = self.calculate_ema(close, 35)[-1]
        trend_zone_upper = k + rma * 0.5
        return trend_zone_upper

    def trigger_candle_45_per(self, open, high, low, close, shadow_range):
        a = abs(high - low)
        b = abs(close - open)
        c = shadow_range / 100

        rv = b < c * a

        x = low + (c * a)
        y = high - (c * a)

        long_bar = rv == 1 and high > y and close < y and open < y
        short_bar = rv == 1 and low < x and close > x and open > x

        return long_bar, short_bar

    def calcSma(self, data, smaPeriod):
        j = next(i for i, x in enumerate(data) if x is not None)
        our_range = range(len(data))[j + smaPeriod - 1:]
        empty_list = [None] * (j + smaPeriod - 1)
        sub_result = [np.mean(data[i - smaPeriod + 1: i + 1]) for i in our_range]

        return np.array(empty_list + sub_result)


    def get_price(self, SYMBOL):
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={SYMBOL}"
        except Exception as e:
            time.sleep(180)
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={SYMBOL}"
        res = requests.get(url)
        self.current_symbol_price = float(res.json()['price'])
        return self.current_symbol_price

    def get_data(self, SYMBOL):
        url = "https://fapi.binance.com/fapi/v1/klines?symbol={}&interval={}&limit={}".format(SYMBOL, TIME_PERIOD,
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

    def time_dot_round(self, TIME_PERIOD):
        candle_time = int(TIME_PERIOD.replace("m", ""))
        candle_time_seconds = candle_time * 60
        recent_check = candle_time_seconds * 0.04
        minute = datetime.now().minute
        second = datetime.now().second
        micro = datetime.now().microsecond
        time_for_next_candle = ((minute % candle_time) * 60) + second + (micro / 1000000)
        if recent_check > time_for_next_candle:
            print("Time dot Sleep is not Required")
        else:
            print("Time dot Sleep Started", datetime.now())
            time.sleep(candle_time_seconds - time_for_next_candle + 2)
            print("Time dot Sleep End", datetime.now())


    def position_quantity_any_direction(self, SYMBOL, client: Client):
        posInfo = client.position_info()
        for counter in posInfo:
            if counter["symbol"] == SYMBOL:
                quantity = float(counter["positionAmt"])
                return quantity

    def position_quantity(self, SYMBOL, client: Client):
        posInfo = client.position_info()
        for counter in posInfo:
            if counter["symbol"] == SYMBOL:
                quantity = abs(float(counter["positionAmt"]))
                return quantity

    def position_info(self, SYMBOL, client: Client):
        posInfo = client.position_info()

        for counter in posInfo:
            if counter["symbol"] == SYMBOL:
                print(counter)
                return counter

    def executed_order_on_wick_check(self,  SYMBOL, client: Client, QNTY):
        self.time_dot_round(TIME_PERIOD=TIME_PERIOD)
        time.sleep(TIME_SLEEP)
        start_price, high, low, close = self.get_data(SYMBOL)
        start_price = np.array(start_price)
        high = np.array(high)
        low = np.array(low)
        close = np.array(close)
        if self.isLongOrderInProgress:
            if high.take(-2) > self.place_order_price > close.take(-2):
                self.cancel_executed_orders(SYMBOL, client, QNTY)
                self.update_data_set(side="LongHitWick", SYMBOL=SYMBOL, client=client, QNTY=QNTY)
        elif self.isShortOrderInProgress:
            if low.take(-2) < self.place_order_price < close.take(-2):
                self.cancel_executed_orders(SYMBOL, client, QNTY)
                self.update_data_set(side="ShortHitWick", SYMBOL=SYMBOL, client=client, QNTY=QNTY)







