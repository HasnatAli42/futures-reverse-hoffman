import numpy as np

from Classes import Symbols, TradingBot, Indicator, Counters
from datetime import datetime

from Classes.DB import track_orders
from Dictionary.Strings import long_placed, null_order, price_over_price, long, short, short_placed
from Functions.Order_Prices import place_order_price, calculate_stop_loss


def check_order(trade_bot_obj: TradingBot, symbol_obj: Symbols, indicator_obj: Indicator, counter_obj: Counters, open_price, high,
                low, close):
    print("\n--------- Currency ---------")
    print(symbol_obj.current_symbol, ":", trade_bot_obj.currency_price)
    print("----------------------------")
    print("\n************** Strategy Result Getting Order Number ", trade_bot_obj.order_sequence,
          " ***********", datetime.now(), "***********")
    if indicator_obj.slow_speed_line > indicator_obj.fast_primary_trend_line:
        if indicator_obj.trend_line_1 >= indicator_obj.fast_primary_trend_line or indicator_obj.trend_line_2 >= indicator_obj.fast_primary_trend_line or indicator_obj.trend_line_3 >= indicator_obj.fast_primary_trend_line or indicator_obj.no_trend_zone_middle_line >= indicator_obj.fast_primary_trend_line:
            print("Long Crossed But lines in between")
        elif indicator_obj.number_of_true_candles(open_price=open_price, high=high, low=low, close=close) < 2:
            print("Long Crossed But True Candles are less then 2")
        else:
            print("Long Crossed looking for Hoffman Long signal wicked candle")
            print("Hoffman Long Signal:", indicator_obj.long_signal_candle)
            print("True candles Before Crossing:", indicator_obj.number_of_true_candles(open_price=open_price,
                                                                                        high=high,
                                                                                        low=low, close=close))
            if indicator_obj.long_signal_candle:
                trade_bot_obj.high_price = np.array(high)[-2]
                trade_bot_obj.place_order_price = place_order_price(side=short, price=trade_bot_obj.high_price,
                                                                    round_value=symbol_obj.current_decimal_point_price)
                trade_bot_obj.trailing_order_price = trade_bot_obj.place_order_price
                trade_bot_obj.stop_loss = calculate_stop_loss(side=short, price=trade_bot_obj.place_order_price,
                                                              indicator_value=indicator_obj.fast_primary_trend_line)
                trade_bot_obj.take_profit = trade_bot_obj.stop_loss * trade_bot_obj.profit_ratio
                if trade_bot_obj.currency_price < trade_bot_obj.place_order_price:
                    order = trade_bot_obj.place_short_order(short=trade_bot_obj.place_order_price,
                                                            SYMBOL=symbol_obj.current_symbol,
                                                            client=symbol_obj.client(),
                                                            Decimal_point_price=symbol_obj.current_decimal_point_price,
                                                            QNTY=symbol_obj.current_QNTY)
                    trade_bot_obj.update_data_set(side="LongOrderPlaced", SYMBOL=symbol_obj.current_symbol,
                                                  client=symbol_obj.client(), QNTY=symbol_obj.current_QNTY)
                    track_orders(order_type=short_placed, symbol=symbol_obj.current_symbol, order1=order,
                                 order2=null_order)
                    trade_bot_obj.write_to_file(currentIndex=symbol_obj.current_index)
                    counter_obj.isProfitCheckPerformed = False
                else:
                    print(price_over_price)
    else:
        if indicator_obj.trend_line_1 <= indicator_obj.fast_primary_trend_line or indicator_obj.trend_line_2 <= indicator_obj.fast_primary_trend_line or indicator_obj.trend_line_3 <= indicator_obj.fast_primary_trend_line or indicator_obj.no_trend_zone_middle_line <= indicator_obj.fast_primary_trend_line:
            print("Short Crossed But lines in between")
        elif indicator_obj.number_of_true_candles(open_price=open_price, high=high, low=low, close=close) < 2:
            print("Long Crossed But True Candles are less then 2")
        else:
            print("Short Crossed looking for Hoffman Short signal wicked candle")
            print("Hoffman Short Signal:", indicator_obj.short_signal_candle)
            print("True candles Before Crossing:", indicator_obj.number_of_true_candles(open_price=open_price,
                                                                                        high=high,
                                                                                        low=low, close=close))
            if indicator_obj.short_signal_candle:
                trade_bot_obj.low_price = np.array(low)[-2]
                trade_bot_obj.place_order_price = place_order_price(side=long, price=trade_bot_obj.low_price,
                                                                    round_value=symbol_obj.current_decimal_point_price)
                trade_bot_obj.trailing_order_price = trade_bot_obj.place_order_price
                trade_bot_obj.stop_loss = calculate_stop_loss(side=long, price=trade_bot_obj.place_order_price,
                                                              indicator_value=indicator_obj.fast_primary_trend_line)
                trade_bot_obj.take_profit = trade_bot_obj.stop_loss * trade_bot_obj.profit_ratio
                if trade_bot_obj.currency_price > trade_bot_obj.place_order_price:
                    order = trade_bot_obj.place_long_order(long=trade_bot_obj.place_order_price,
                                                           SYMBOL=symbol_obj.current_symbol, client=symbol_obj.client(),
                                                           Decimal_point_price=symbol_obj.current_decimal_point_price,
                                                           QNTY=symbol_obj.current_QNTY)
                    trade_bot_obj.update_data_set(side="ShortOrderPlaced", SYMBOL=symbol_obj.current_symbol,
                                                  client=symbol_obj.client(), QNTY=symbol_obj.current_QNTY)
                    track_orders(order_type=long_placed, symbol=symbol_obj.current_symbol, order1=order,
                                 order2=null_order)
                    trade_bot_obj.write_to_file(currentIndex=symbol_obj.current_index)
                    counter_obj.isProfitCheckPerformed = False
                else:
                    print(price_over_price)
