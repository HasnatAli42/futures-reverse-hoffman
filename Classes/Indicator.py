import numpy as np
import talib


class Indicator:
    def __init__(self):
        self.slow_speed_line = 0
        self.fast_primary_trend_line = 0
        self.trend_line_1 = 0
        self.trend_line_2 = 0
        self.trend_line_3 = 0
        self.no_trend_zone_middle_line = 0
        self.long_signal_candle = False
        self.short_signal_candle = False
        self.EMA_LOW_TIME_FRAME = 0
        self.EMA_HIGH_TIME_FRAME = 0
        self.isBullishTrend = False
        self.isBearishTrend = False
        self.isDinRange = False
#        self.no_trend_zone_upper_line = trade_bot_obj.upper_and_lower_trend_zone_line(high, low, close) + 2.6

    def trigger_candle_45_per(self, open, high, low, close, shadow_range):
        a = abs(high - low)
        b = abs(close - open)
        c = shadow_range / 100
        rv = b < c * a
        x = low + (c * a)
        y = high - (c * a)

        long_bar = rv == 1 and high > y > close and open < y
        short_bar = rv == 1 and low < x < close and open > x

        return long_bar, short_bar

    def calculate(self, open_price, high, low, close):
        close = np.array(close)
        self.slow_speed_line = talib.SMA(close, 5)[-1]
        self.fast_primary_trend_line = talib.EMA(close, 18)[-1]
        self.trend_line_1 = talib.SMA(close, 50)[-1]
        self.trend_line_2 = talib.SMA(close, 89)[-1]
        self.trend_line_3 = talib.EMA(close, 144)[-1]
        self.no_trend_zone_middle_line = talib.EMA(close, 35)[-1]
        self.long_signal_candle, self.short_signal_candle = self.trigger_candle_45_per(np.array(open_price)[-2],
                                                                                       np.array(high)[-2],
                                                                                       np.array(low)[-2],
                                                                                       np.array(close)[-2], 45)

    def crossing_index_check(self, close):
        close = np.array(close)
        index_counter = -1
        if self.slow_speed_line > self.fast_primary_trend_line:
            slow_speed_line = 1
            fast_primary_trend_line = 0
            while slow_speed_line > fast_primary_trend_line:
                index_counter += -1
                slow_speed_line = talib.SMA(close, 5)[index_counter]
                fast_primary_trend_line = talib.EMA(close, 18)[index_counter]
        else:
            slow_speed_line = 0
            fast_primary_trend_line = 1
            while slow_speed_line < fast_primary_trend_line:
                index_counter += -1
                slow_speed_line = talib.SMA(close, 5)[index_counter]
                fast_primary_trend_line = talib.EMA(close, 18)[index_counter]
        return index_counter + 1

    def number_of_true_candles(self, open_price, high, low, close):
        crossing_index = self.crossing_index_check(close=close)
        true_candles = []
        if crossing_index < -4:
            if self.slow_speed_line > self.fast_primary_trend_line:
                for index in range(-3, crossing_index, -1):
                    long_candle, short_candle = self.trigger_candle_45_per(np.array(open_price)[index],
                                                                           np.array(high)[index],
                                                                           np.array(low)[index],
                                                                           np.array(close)[index], 45)
                    if long_candle:
                        true_candles.append(1)

            else:
                for index in range(-3, self.crossing_index_check(close=close), -1):
                    long_candle, short_candle = self.trigger_candle_45_per(np.array(open_price)[index],
                                                                           np.array(high)[index],
                                                                           np.array(low)[index],
                                                                           np.array(close)[index], 45)
                    if short_candle:
                        true_candles.append(1)
        return len(true_candles)

    def analyze_trend(self, close):
        close = np.array(close)
        self.EMA_LOW_TIME_FRAME = talib.EMA(close, 50)[-1]
        self.EMA_HIGH_TIME_FRAME = talib.EMA(close, 100)[-1]
        if self.EMA_LOW_TIME_FRAME >= self.EMA_HIGH_TIME_FRAME:
            self.isBullishTrend = True
            self.isBearishTrend = False
        elif self.EMA_LOW_TIME_FRAME < self.EMA_HIGH_TIME_FRAME:
            self.isBearishTrend = True
            self.isBullishTrend = False


    def first_print(self, currency_price, SYMBOL):
        print("\n--------- Currency ---------")
        print(SYMBOL, ":", currency_price)
        print("----------------------------")
        print("\n************** Strategy Result First Run ***********")
        print("Slow Speed Line: ", self.slow_speed_line)
        print("Fast Primary Trend Line: ", self.fast_primary_trend_line)
        print("Trend Line - 1: ", self.trend_line_1)
        print("Trend Line - 2: ", self.trend_line_2)
        print("Trend Line - 3: ", self.trend_line_3)
        print("No Trend Zone - Middle: ", self.no_trend_zone_middle_line)
        print("Long Signal: ", self.long_signal_candle, "Short Signal: ", self.short_signal_candle)
        # print("Last Candle High:",np.array(high)[-2])
        # print("Higher Order:", round(np.array(high)[-2]+(np.array(high)[-2] * above_or_below_wick/100),2))
        # print("Last Candle Low:", np.array(low)[-2])
        # print("Lower Order:", round(np.array(low)[-2]-(np.array(low)[-2] * above_or_below_wick/100),2))



