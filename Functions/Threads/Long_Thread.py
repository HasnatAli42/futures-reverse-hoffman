import threading

import numpy as np

from BinanceFuturesPy.futurespy import Client
from Classes.DB import threads_exception_data, track_orders
from Classes.Indicator import Indicator
from Classes.Symbols import Symbols
from Classes.TradingBot import TradingBot
from Config.Settings import above_or_below_wick, max_take_profit_limit, TIME_PERIOD, TIME_SLEEP
from Dictionary.Strings import long_limits_placed, long_limits_placed_exception
from Functions.Mappers import assign_trade_bot_initialize_thread, assign_indicate_obj, assign_trade_bot_close_thread
import time


def long_order_placed(
        t_obj: TradingBot,
        i_obj: Indicator,
        s_obj: Symbols,
        current_symbol,
        current_decimal_point_price,
        current_QNTY,
        current_index,
        client: Client,
        is_this_thread_executed,
):
    try:
        t_obj.threadCounter += 1
        print("Thread ", threading.current_thread(), "started with symbol = ", current_symbol)
        thread_trade_obj = TradingBot()
        assign_trade_bot_initialize_thread(to_be_assigned=thread_trade_obj, assigned_from=t_obj)
        thread_indicate_obj = Indicator()
        assign_indicate_obj(to_be_assigned_ind_obj=thread_indicate_obj, assigned_from_ind_obj=i_obj)

        while t_obj.isThreadAllowed:
            open_price, high, low, close = thread_trade_obj.get_data(SYMBOL=current_symbol)
            thread_indicate_obj.calculate(open_price=open_price, high=high, low=low, close=close)
            thread_trade_obj.currency_price = thread_trade_obj.get_price(SYMBOL=current_symbol)

            if not thread_indicate_obj.short_signal_candle:
                thread_trade_obj.newHoffmanSignalCheck = True
            if thread_indicate_obj.short_signal_candle:
                thread_trade_obj.newHoffmanSignalCheck = False
                thread_trade_obj.low_price = np.array(low)[-2]
                thread_trade_obj.new_place_order_price = round(
                    thread_trade_obj.low_price - (thread_trade_obj.low_price * above_or_below_wick / 100),
                    current_decimal_point_price)
                if thread_trade_obj.new_place_order_price != thread_trade_obj.place_order_price:
                    client.cancel_all_open_orders(current_symbol)
                    thread_trade_obj.place_order_price = thread_trade_obj.new_place_order_price
                    thread_trade_obj.place_long_order(short=thread_trade_obj.place_order_price,
                                                       SYMBOL=current_symbol, client=client,
                                                       Decimal_point_price=current_decimal_point_price,
                                                       QNTY=current_QNTY)
                    thread_trade_obj.stop_loss = (thread_indicate_obj.fast_primary_trend_line - thread_trade_obj.place_order_price) / thread_trade_obj.place_order_price * 100
                    thread_trade_obj.take_profit = thread_trade_obj.stop_loss * thread_trade_obj.profit_ratio
                    thread_trade_obj.update_data_set(side="ShortUpdated", SYMBOL=current_symbol,
                                                     client=client, QNTY=current_QNTY)
                    thread_trade_obj.write_to_file(currentIndex=current_index)
            if thread_trade_obj.position_quantity(SYMBOL=current_symbol, client=client) > 0:
                print("Order Executed Successfully for",current_symbol)
                thread_trade_obj.update_data_set(side="ShortExecuted", SYMBOL=current_symbol,
                                                 client=client, QNTY=current_QNTY)
                order1, order2, error = thread_trade_obj.place_in_progress_order_limits(SYMBOL=current_symbol,
                                                                                        client=client,
                                                                                        Decimal_point_price=
                                                                                        current_decimal_point_price,
                                                                                        QNTY=current_QNTY)
                if error:
                    track_orders(order_type=long_limits_placed, symbol=current_symbol, order1=order1,
                                 order2=order2)
                elif not error:
                    track_orders(order_type=long_limits_placed_exception, symbol=current_symbol, order1=order1,
                                 order2=order2)
                thread_trade_obj.write_to_file(currentIndex=current_index)
                t_obj.isThreadAllowed = False
                t_obj.wasThreadLong = True
                assign_trade_bot_close_thread(to_be_assigned=t_obj, assigned_from=thread_trade_obj)
                t_obj.order_executed_for_symbol = current_symbol
                break
            if thread_indicate_obj.slow_speed_line > thread_indicate_obj.fast_primary_trend_line or thread_trade_obj.take_profit > max_take_profit_limit:
                print("Order Cancelled Successfully for", current_symbol)
                client.cancel_all_open_orders(current_symbol)
                thread_trade_obj.newHoffmanSignalCheck = False
                if thread_trade_obj.take_profit > max_take_profit_limit:
                    thread_trade_obj.update_data_set(side="ShortCancelledHigh", SYMBOL=current_symbol,
                                                     client=client, QNTY=current_QNTY)
                else:
                    thread_trade_obj.update_data_set(side="ShortCancelled", SYMBOL=current_symbol,
                                                     client=client, QNTY=current_QNTY)
                thread_trade_obj.write_to_file(currentIndex=current_index)
                thread_trade_obj.time_dot_round(TIME_PERIOD=TIME_PERIOD)
                break
            if t_obj.isThreadAllowed:
                time.sleep(TIME_SLEEP * 3)
        t_obj.threadCounter += -1
    except Exception as short_thread_exception:
        cancel_order = client.cancel_all_open_orders(current_symbol)
        threads_exception_data(symbol=current_symbol, exception=short_thread_exception, order=cancel_order)
        t_obj.threadCounter += -1