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
        self.X = 0
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0
#        self.no_trend_zone_upper_line = trade_bot_obj.upper_and_lower_trend_zone_line(high, low, close) + 2.6

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

    def calculate_range(self, provided_array_higher,provided_array_lower, check_nearest):
        global provided_array
        provided_array_higher = np.array(provided_array_higher)
        provided_array_lower = np.array(provided_array_lower)
        for current_index in range(0, len(provided_array_higher)-1, 1):
            if not provided_array_higher[current_index] > provided_array_lower[current_index]:
                swap = provided_array_higher[current_index]
                provided_array_higher[current_index] = provided_array_lower[current_index]
                provided_array_lower[current_index] = swap
        if self.isBullishTrend:
            provided_array = np.array(provided_array_lower)
        elif self.isBearishTrend:
            provided_array = np.array(provided_array_higher)
        for x in range(-check_nearest, 0, 1):
            if provided_array[x] == self.D:
                self.isDinRange = True
                break
            else:
                self.isDinRange = False

    def find_x_a_b_c_d(self, open_price, high, low, close, find_range):
        global index, x,a,b,c,d
        high = np.array(open_price)
        low = np.array(close)
        for current_range in range(0, len(high)-1, 1):
            if high[current_range] > low[current_range]:
                pass
            else:
                swap = high[current_range]
                high[current_range] = low[current_range]
                low[current_range] = swap

        if self.isBullishTrend:
            current_range = find_range
            d = low[-1]
            for current_index in range(len(low)-1, 0, -1):
                if low[current_index]< d:
                    # print("D Swapped at index = ",current_index)
                    d = low[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bullish D bottom current = ", d, "comparing with", low[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range -1
                        self.D = d
                        # print("Found D = ",self.D," at index =",index)
                        break
            current_range = find_range
            c = high[index]
            for current_index in range(index-1,0,-1):
                if high[current_index] > c:
                    # print("C Swapped at index = ",current_index)
                    c = high[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bullish C top current = ", c, "comparing with", high[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range
                        self.C = c
                        # print("Found C = ", self.C, " at index =", index)
                        break
            current_range = find_range
            b = low[index]
            for current_index in range(index - 1, 0, -1):
                if low[current_index] < b:
                    # print("B Swapped at index = ",current_index)
                    b = low[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bullish B bottom current = ", b, "comparing with", low[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range
                        self.B = b
                        # print("Found B = ", self.B, " at index =", index)
                        break
            current_range = find_range
            a = high[index]
            for current_index in range(index - 1, 0, -1):
                if high[current_index] > a:
                    # print("A Swapped at index = ",current_index)
                    a = high[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bullish A top current = ", a, "comparing with", high[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range
                        self.A = a
                        # print("Found A = ", self.A, " at index =", index)
                        break
            current_range = find_range
            x = low[index]
            for current_index in range(index - 1, 0, -1):
                if low[current_index] < x:
                    # print("X Swapped at index = ",current_index)
                    x = low[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bullish X bottom current = ", x, "comparing with", low[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range
                        self.X = x
                        # print("Found X = ", self.X, " at index =", index)
                        break

        elif self.isBearishTrend:
            current_range = find_range
            d = high[-1]
            for current_index in range(len(high) - 1, 0, -1):
                if high[current_index] > d:
                    # print("D Swapped at index = ",current_index)
                    d = high[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bearish D top current = ", d, "comparing with", high[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range-1
                        self.D = d
                        # print("Found D = ", self.D, " at index =", index)
                        break
            current_range = find_range
            c = low[index]
            for current_index in range(index - 1, 0, -1):
                if low[current_index] < c:
                    # print("C Swapped at index = ",current_index)
                    c = low[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bearish C bottom current = ", c, "comparing with", low[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range
                        self.C = c
                        # print("Found C = ", self.C, " at index =", index)
                        break
            current_range = find_range
            b = high[index]
            for current_index in range(index - 1, 0, -1):
                if high[current_index] > b:
                    # print("B Swapped at index = ",current_index)
                    b = high[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bearish B top current = ", b, "comparing with", high[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range
                        self.B = b
                        # print("Found B = ", self.B, " at index =", index)
                        break
            current_range = find_range
            a = low[index]
            for current_index in range(index - 1, 0, -1):
                if low[current_index] < a:
                    # print("A Swapped at index = ",current_index)
                    a = low[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bearish A bottom current = ", a, "comparing with", low[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range
                        self.A = a
                        # print("Found A = ", self.A, " at index =", index)
                        break
            current_range = find_range
            x = high[index]
            for current_index in range(index - 1, 0, -1):
                if high[current_index] > x:
                    # print("X Swapped at index = ",current_index)
                    x = high[current_index]
                    current_range = find_range
                else:
                    # print("Finding Bearish X top current = ", x, "comparing with", high[current_index], "at index = ",
                    #       current_index, "with range =", current_range)
                    current_range += -1
                    if current_range == 0:
                        index = current_index + find_range
                        self.X = x
                        # print("Found X = ", self.X, " at index =", index)
                        break

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

    def print_x_a_b_c_d(self):
        print("X = ", self.X)
        print("A = ", self.A)
        print("B = ", self.B)
        print("C = ", self.C)
        print("D = ", self.D)

