from datetime import datetime
import time
import numpy as np
import threading
from Classes.Counters import Counters
from Classes.DB import DB, threads_exception_data
from Classes.Indicator import Indicator
from Classes.Symbols import Symbols
from Classes.TradingBot import TradingBot
from Classes.Settings import above_or_below_wick, TIME_PERIOD, TIME_SLEEP, max_take_profit_limit
from BinanceFuturesPy.futurespy import Client


def assign_trade_bot_initialize_thread(to_be_assigned: TradingBot, assigned_from: TradingBot):
    to_be_assigned.currency_price = assigned_from.currency_price
    to_be_assigned.high_price = assigned_from.high_price
    to_be_assigned.take_profit = assigned_from.take_profit
    to_be_assigned.stop_loss = assigned_from.stop_loss
    to_be_assigned.newHoffmanSignalCheck = assigned_from.newHoffmanSignalCheck
    to_be_assigned.new_place_order_price = assigned_from.new_place_order_price
    to_be_assigned.place_order_price = assigned_from.place_order_price


def assign_trade_bot_close_thread(to_be_assigned: TradingBot, assigned_from: TradingBot):
    to_be_assigned.thread_currency_price = assigned_from.currency_price
    to_be_assigned.thread_high_price = assigned_from.high_price
    to_be_assigned.thread_take_profit = assigned_from.take_profit
    to_be_assigned.thread_stop_loss = assigned_from.stop_loss
    to_be_assigned.thread_newHoffmanSignalCheck = assigned_from.newHoffmanSignalCheck
    to_be_assigned.thread_new_place_order_price = assigned_from.new_place_order_price
    to_be_assigned.thread_place_order_price = assigned_from.place_order_price


def assign_trade_bot_main_open(to_be_assigned: TradingBot):
    to_be_assigned.currency_price = to_be_assigned.thread_currency_price
    to_be_assigned.high_price = to_be_assigned.thread_high_price
    to_be_assigned.take_profit = to_be_assigned.thread_take_profit
    to_be_assigned.stop_loss = to_be_assigned.thread_stop_loss
    to_be_assigned.newHoffmanSignalCheck = to_be_assigned.thread_newHoffmanSignalCheck
    to_be_assigned.new_place_order_price = to_be_assigned.thread_new_place_order_price
    to_be_assigned.place_order_price = to_be_assigned.thread_place_order_price
    to_be_assigned.trailing_order_price = to_be_assigned.thread_place_order_price


def assign_indicate_obj(to_be_assigned_ind_obj: Indicator, assigned_from_ind_obj: Indicator):
    to_be_assigned_ind_obj.long_signal_candle = assigned_from_ind_obj.long_signal_candle
    to_be_assigned_ind_obj.slow_speed_line = assigned_from_ind_obj.slow_speed_line
    to_be_assigned_ind_obj.fast_primary_trend_line = assigned_from_ind_obj.fast_primary_trend_line


def allow_thread(t_obj: TradingBot):
    time.sleep(TIME_SLEEP*4)
    t_obj.isThreadAllowed = True


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
        print("Thread ",threading.current_thread(),"started with symbol = ",current_symbol)
        thread_trade_obj = TradingBot()
        assign_trade_bot_initialize_thread(to_be_assigned=thread_trade_obj, assigned_from=t_obj)
        thread_indicate_obj = Indicator()
        assign_indicate_obj(to_be_assigned_ind_obj=thread_indicate_obj, assigned_from_ind_obj=i_obj)

        while t_obj.isThreadAllowed:
            open_price, high, low, close = thread_trade_obj.get_data(SYMBOL=current_symbol)
            thread_indicate_obj.calculate(open_price=open_price, high=high, low=low, close=close)
            thread_trade_obj.currency_price = thread_trade_obj.get_price(SYMBOL=current_symbol)
            # print("\n--------- Currency ---------")
            # print(current_symbol, ":", thread_trade_obj.currency_price)
            # print("\n************** Strategy Result Long Placed at: ",
            #       thread_trade_obj.high_price + (thread_trade_obj.high_price * above_or_below_wick / 100), " ***********",
            #       datetime.now(), "***********")
            # print(f"Take Profit {thread_trade_obj.take_profit} |-------| Stop Loss {thread_trade_obj.stop_loss}")
            if not thread_indicate_obj.long_signal_candle:
                thread_trade_obj.newHoffmanSignalCheck = True
            if thread_indicate_obj.long_signal_candle:
                thread_trade_obj.newHoffmanSignalCheck = False
                thread_trade_obj.high_price = np.array(high)[-2]
                thread_trade_obj.new_place_order_price = round(
                    thread_trade_obj.high_price + (thread_trade_obj.high_price * above_or_below_wick / 100),
                    current_decimal_point_price)
                if thread_trade_obj.new_place_order_price != thread_trade_obj.place_order_price:
                    client.cancel_all_open_orders(current_symbol)
                    thread_trade_obj.place_order_price = thread_trade_obj.new_place_order_price
                    thread_trade_obj.place_long_order(long=thread_trade_obj.place_order_price,
                                                      SYMBOL=current_symbol,
                                                      client=client,
                                                      Decimal_point_price=current_decimal_point_price,
                                                      QNTY=current_QNTY)
                    thread_trade_obj.stop_loss = ((
                                                              thread_trade_obj.place_order_price - thread_indicate_obj.fast_primary_trend_line) / thread_trade_obj.place_order_price) * 100
                    thread_trade_obj.take_profit = thread_trade_obj.stop_loss * thread_trade_obj.profit_ratio
                    thread_trade_obj.update_data_set(side="LongUpdated", SYMBOL=current_symbol,
                                                     client=client,
                                                     QNTY=current_QNTY)
                    thread_trade_obj.write_to_file(currentIndex=current_index)

            if thread_trade_obj.position_quantity(SYMBOL=current_symbol, client=client) > 0:
                print("Order Executed Successfully for", current_symbol)
                thread_trade_obj.update_data_set(side="LongExecuted", SYMBOL=current_symbol,
                                                 client=client,
                                                 QNTY=current_QNTY)
                thread_trade_obj.place_in_progress_order_limits(SYMBOL=current_symbol, client=client,
                                                                Decimal_point_price=current_decimal_point_price,
                                                                QNTY=current_QNTY)
                thread_trade_obj.write_to_file(currentIndex=current_index)
                t_obj.isThreadAllowed = False
                t_obj.wasThreadLong = True
                assign_trade_bot_close_thread(to_be_assigned=t_obj, assigned_from=thread_trade_obj)
                t_obj.order_executed_for_symbol = current_symbol
                break
            if thread_indicate_obj.slow_speed_line < thread_indicate_obj.fast_primary_trend_line or thread_trade_obj.take_profit > max_take_profit_limit:
                print("Order Cancelled Successfully for", current_symbol)
                client.cancel_all_open_orders(current_symbol)
                thread_trade_obj.newHoffmanSignalCheck = False
                if thread_trade_obj.take_profit > max_take_profit_limit:
                    thread_trade_obj.update_data_set(side="LongCancelledHigh", SYMBOL=current_symbol,
                                                     client=client, QNTY=current_QNTY)
                else:
                    thread_trade_obj.update_data_set(side="LongCancelled", SYMBOL=current_symbol,
                                                     client=client, QNTY=current_QNTY)
                thread_trade_obj.write_to_file(currentIndex=current_index)
                thread_trade_obj.time_dot_round(TIME_PERIOD=TIME_PERIOD)
                break
            if t_obj.isThreadAllowed:
                time.sleep(TIME_SLEEP * 3)
        t_obj.threadCounter += -1
    except Exception as long_thread_exception:
        cancel_order = client.cancel_all_open_orders(current_symbol)
        threads_exception_data(symbol=current_symbol, exception=long_thread_exception, order=cancel_order)
        t_obj.threadCounter += -1


def short_order_placed(
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
        print("Thread ", threading.current_thread(), "started with symbol = ", current_symbol)
        thread_trade_obj = TradingBot()
        assign_trade_bot_initialize_thread(to_be_assigned=thread_trade_obj, assigned_from=t_obj)
        thread_indicate_obj = Indicator()
        assign_indicate_obj(to_be_assigned_ind_obj=thread_indicate_obj, assigned_from_ind_obj=i_obj)

        while t_obj.isThreadAllowed:
            open_price, high, low, close = thread_trade_obj.get_data(SYMBOL=current_symbol)
            thread_indicate_obj.calculate(open_price=open_price, high=high, low=low, close=close)
            thread_trade_obj.currency_price = thread_trade_obj.get_price(SYMBOL=current_symbol)
            # print("\n--------- Currency ---------")
            # print(current_symbol, ":", thread_trade_obj.currency_price)
            # print("\n************** Strategy Result Short Placed at: ", thread_trade_obj.place_order_price,
            #       " ***********", datetime.now(), "***********")
            # print(f"Take Profit {thread_trade_obj.take_profit} |-------| Stop Loss {thread_trade_obj.stop_loss}")
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
                    thread_trade_obj.place_short_order(short=thread_trade_obj.place_order_price,
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
                thread_trade_obj.place_in_progress_order_limits(SYMBOL=current_symbol,
                                                                client=client,
                                                                Decimal_point_price=current_decimal_point_price,
                                                                QNTY=current_QNTY)
                thread_trade_obj.write_to_file(currentIndex=current_index)
                t_obj.isThreadAllowed = False
                t_obj.wasThreadShort = True
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


def main(trade_bot_obj: TradingBot, counter_obj: Counters, indicator_obj: Indicator, symb_obj: Symbols, db_obj: DB):
    while True:
        print("")
        print("Current Open Threads By Threads         = ", threading.active_count())
        print("Current Open Thread Details By Threads  =", threading.enumerate())
        print("Current Open Threads        = ", trade_bot_obj.threadCounter)
        print("Current Open Thread Details =", symb_obj.moved_symbols_list)
        print("Symbols List Length         = ", len(symb_obj.symbols))

        if not trade_bot_obj.isThreadAllowed:
            assign_trade_bot_main_open(to_be_assigned=trade_bot_obj)
            cancel_all_orders = threading.Thread(name="cancel_all_orders", target=symb_obj.cancel_all_orders, args=("fake_argument1", "fake_argument1", "fake_argument1"))
            cancel_all_orders.start()
            symb_obj.reset_increment_to_specific_symbol(symbol=trade_bot_obj.order_executed_for_symbol)
            executed_order_on_wick_check = threading.Thread(name="executed_order_on_wick_check", target=trade_bot_obj.executed_order_on_wick_check, args=(symb_obj.current_symbol, symb_obj.client(), symb_obj.current_QNTY))
            executed_order_on_wick_check.start()
            allow_thread(t_obj=trade_bot_obj)
            if trade_bot_obj.wasThreadLong:
                trade_bot_obj.wasThreadLong = False
                trade_bot_obj.isOrderInProgress = True
                trade_bot_obj.isLongOrderInProgress = True
            elif trade_bot_obj.wasThreadShort:
                trade_bot_obj.wasThreadShort = False
                trade_bot_obj.isOrderInProgress = True
                trade_bot_obj.isShortOrderInProgress = True

        db_obj.initialize_db(symb_obj.current_symbol)
        open_price, high, low, close = symb_obj.get_data(timeframe=TIME_PERIOD)
        indicator_obj.calculate(open_price=open_price, high=high, low=low, close=close)
        trade_bot_obj.currency_price = symb_obj.get_price()

        if trade_bot_obj.Highest_Price < trade_bot_obj.currency_price:
            trade_bot_obj.Highest_Price = trade_bot_obj.currency_price
        if trade_bot_obj.LowestPrice > trade_bot_obj.currency_price:
            trade_bot_obj.LowestPrice = trade_bot_obj.currency_price

        if trade_bot_obj.firstRun:
            trade_bot_obj.firstRun = False
            indicator_obj.first_print(trade_bot_obj.currency_price, symb_obj.current_symbol)

        else:
            if trade_bot_obj.isOrderPlaced and trade_bot_obj.isLongOrderPlaced:

                placed_order_execution_check = threading.Thread(name=symb_obj.current_symbol, target=long_order_placed, args=(
                        trade_bot_obj, indicator_obj, symb_obj, symb_obj.current_symbol, symb_obj.current_decimal_point_price,
                        symb_obj.current_QNTY, symb_obj.current_index, symb_obj.client(), False))
                placed_order_execution_check.start()
                trade_bot_obj.threadCounter += 1
                time.sleep(TIME_SLEEP)
                trade_bot_obj.isOrderPlaced = False
                trade_bot_obj.isLongOrderPlaced = False
                symb_obj.move_symbols()

            elif trade_bot_obj.isOrderPlaced and trade_bot_obj.isShortOrderPlaced:
                placed_order_execution_check = threading.Thread(name=symb_obj.current_symbol, target=short_order_placed, args=(
                        trade_bot_obj, indicator_obj, symb_obj, symb_obj.current_symbol, symb_obj.current_decimal_point_price,
                        symb_obj.current_QNTY, symb_obj.current_index, symb_obj.client(), False))
                placed_order_execution_check.start()
                trade_bot_obj.threadCounter += 1
                time.sleep(TIME_SLEEP)
                trade_bot_obj.isOrderPlaced = False
                trade_bot_obj.isShortOrderPlaced = False
                symb_obj.move_symbols()

            elif trade_bot_obj.isOrderInProgress and trade_bot_obj.isLongOrderInProgress:
                if trade_bot_obj.currency_price < trade_bot_obj.place_order_price:
                    if counter_obj.isInProfit:
                        counter_obj.isInProfit = False
                        counter_obj.long_profit_counter_list.append(counter_obj.long_current_in_profit_counter)
                        if len(counter_obj.long_profit_counter_list) == 1 and len(
                                counter_obj.long_loss_counter_list) == 0:
                            counter_obj.isProfitFirst = True
                        counter_obj.long_current_in_profit_counter = 0
                    counter_obj.long_current_in_loss_counter += 1
                    counter_obj.isInLoss = True
                    counter_obj.long_total_in_loss_counter += 1

                else:
                    if counter_obj.isInLoss:
                        counter_obj.isInLoss = False
                        counter_obj.long_loss_counter_list.append(counter_obj.long_current_in_loss_counter)
                        if len(counter_obj.long_profit_counter_list) == 0 and len(
                                counter_obj.long_loss_counter_list) == 1:
                            counter_obj.isLossFirst = True
                        counter_obj.long_current_in_loss_counter = 0
                    counter_obj.long_current_in_profit_counter += 1
                    counter_obj.isInProfit = True
                    counter_obj.long_total_in_profit_counter += 1

                print("\n--------- Currency ---------")
                print(symb_obj.current_symbol, ":", trade_bot_obj.currency_price)
                print("Take Profit:",
                      trade_bot_obj.place_order_price + (trade_bot_obj.place_order_price * trade_bot_obj.take_profit
                                                         / 100))
                print("Stop Loss:",
                      trade_bot_obj.place_order_price - (trade_bot_obj.place_order_price * trade_bot_obj.stop_loss /
                                                         100))
                print("\n************** Strategy Result Long In Progress ***********", datetime.now(), "***********")
                counter_obj.long_print()
                trade_bot_obj.place_trailing_stop_loss(SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                                                       Decimal_point_price=symb_obj.current_decimal_point_price,
                                                       QNTY=symb_obj.current_QNTY)

                if counter_obj.is_order_in_profit_again(side="buy") and not counter_obj.isProfitCheckPerformed:
                    trade_bot_obj.trailing_stop_loss_order(stop_loss_price=trade_bot_obj.place_order_price,
                                                           SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                                                           Decimal_point_price=symb_obj.current_decimal_point_price,
                                                           QNTY=symb_obj.current_QNTY)
                    trade_bot_obj.isBreakEvenCalled = True
                    counter_obj.isProfitCheckPerformed = True

                if trade_bot_obj.isBreakEvenCalled:
                    if trade_bot_obj.currency_price > trade_bot_obj.place_order_price + (
                            trade_bot_obj.place_order_price * 0.0015):
                        trade_bot_obj.trailing_stop_loss_order(
                            stop_loss_price=trade_bot_obj.place_order_price + (trade_bot_obj.place_order_price * 0.001),
                            SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                            Decimal_point_price=symb_obj.current_decimal_point_price, QNTY=symb_obj.current_QNTY)
                        trade_bot_obj.isBreakEvenCalled = False

                if trade_bot_obj.position_quantity(SYMBOL=symb_obj.current_symbol, client=symb_obj.client()) == 0:
                    symb_obj.client().cancel_all_open_orders(symb_obj.current_symbol)
                    if trade_bot_obj.LongHit == "LongHit" and trade_bot_obj.currency_price > trade_bot_obj.place_order_price:
                        trade_bot_obj.LongHit = "LongHitProfit"
                    elif trade_bot_obj.LongHit == "LongHit" and trade_bot_obj.currency_price < trade_bot_obj.place_order_price:
                        trade_bot_obj.LongHit = "LongHitLoss"
                    trade_bot_obj.isOrderInProgress = False
                    trade_bot_obj.isLongOrderInProgress = False
                    trade_bot_obj.isBreakEvenCalled = False
                    trade_bot_obj.order_sequence += 1
                    trade_bot_obj.update_data_set(side=trade_bot_obj.LongHit, SYMBOL=symb_obj.current_symbol,
                                                  client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                    counter_obj.update_data_set_tickers(side="buy", SYMBOL=symb_obj.current_symbol,
                                                        LongHit=trade_bot_obj.LongHit,
                                                        ShortHit=trade_bot_obj.ShortHit,
                                                        order_sequence=trade_bot_obj.order_sequence,
                                                        place_order_price=trade_bot_obj.place_order_price,
                                                        currency_price=trade_bot_obj.currency_price)
                    counter_obj.long_clear()
                    trade_bot_obj.LongHit = "LongHit"
                    trade_bot_obj.write_to_file(currentIndex=symb_obj.current_index)
                if indicator_obj.slow_speed_line < indicator_obj.fast_primary_trend_line:
                    print("Order In-Progress Cancelled Successfully")
                    trade_bot_obj.LongHit = "LongHitCrossing"
                    trade_bot_obj.isOrderInProgress = False
                    trade_bot_obj.isLongOrderInProgress = False
                    trade_bot_obj.isBreakEvenCalled = False
                    trade_bot_obj.cancel_executed_orders(SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                                                         QNTY=symb_obj.current_QNTY)
                    trade_bot_obj.order_sequence += 1
                    trade_bot_obj.update_data_set(side=trade_bot_obj.LongHit, SYMBOL=symb_obj.current_symbol,
                                                  client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                    counter_obj.update_data_set_tickers(side="buy", SYMBOL=symb_obj.current_symbol,
                                                        LongHit=trade_bot_obj.LongHit,
                                                        ShortHit=trade_bot_obj.ShortHit,
                                                        order_sequence=trade_bot_obj.order_sequence,
                                                        place_order_price=trade_bot_obj.place_order_price,
                                                        currency_price=trade_bot_obj.currency_price)
                    counter_obj.long_clear()
                    trade_bot_obj.LongHit = "LongHit"
                    trade_bot_obj.write_to_file(currentIndex=symb_obj.current_index)
                if not trade_bot_obj.isOrderInProgress and not trade_bot_obj.isLongOrderInProgress:
                    print("Long Order Sleep Time is Called")
                    trade_bot_obj.update_data_set(side="sleep started", SYMBOL=symb_obj.current_symbol,
                                                  client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                    trade_bot_obj.time_dot_round(TIME_PERIOD)
                    trade_bot_obj.update_data_set(side="sleep ended", SYMBOL=symb_obj.current_symbol,
                                                  client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                    symb_obj.increment()
            elif trade_bot_obj.isOrderInProgress and trade_bot_obj.isShortOrderInProgress:
                if trade_bot_obj.currency_price > trade_bot_obj.place_order_price:
                    if counter_obj.isInProfit:
                        counter_obj.isInProfit = False
                        counter_obj.short_profit_counter_list.append(counter_obj.short_current_in_profit_counter)
                        if len(counter_obj.short_profit_counter_list) == 1 and len(
                                counter_obj.short_loss_counter_list) == 0:
                            counter_obj.isProfitFirst = True

                        counter_obj.short_current_in_profit_counter = 0
                    counter_obj.short_current_in_loss_counter += 1
                    counter_obj.isInLoss = True
                    counter_obj.short_total_in_loss_counter += 1
                else:
                    if counter_obj.isInLoss:
                        counter_obj.isInLoss = False
                        counter_obj.short_loss_counter_list.append(counter_obj.short_current_in_loss_counter)
                        if len(counter_obj.short_profit_counter_list) == 0 and len(
                                counter_obj.short_loss_counter_list) == 1:
                            counter_obj.isLossFirst = True

                        counter_obj.short_current_in_loss_counter = 0
                    counter_obj.short_current_in_profit_counter += 1
                    counter_obj.isInProfit = True
                    counter_obj.short_total_in_profit_counter += 1

                print("\n--------- Currency ---------")
                print(symb_obj.current_symbol, ":", trade_bot_obj.currency_price)
                print("Take Profit:",
                      trade_bot_obj.place_order_price - (trade_bot_obj.place_order_price * trade_bot_obj.take_profit
                                                         / 100))
                print("Stop Loss:",
                      trade_bot_obj.place_order_price + (trade_bot_obj.place_order_price * trade_bot_obj.stop_loss /
                                                         100))
                print("\n************** Strategy Result Short In Progress ***********", datetime.now(), "***********")
                counter_obj.short_print()
                trade_bot_obj.place_trailing_stop_loss(SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                                                       Decimal_point_price=symb_obj.current_decimal_point_price,
                                                       QNTY=symb_obj.current_QNTY)

                if counter_obj.is_order_in_profit_again(side="sell") and not counter_obj.isProfitCheckPerformed:
                    trade_bot_obj.trailing_stop_loss_order(stop_loss_price=trade_bot_obj.place_order_price,
                                                           SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                                                           Decimal_point_price=symb_obj.current_decimal_point_price,
                                                           QNTY=symb_obj.current_QNTY)
                    trade_bot_obj.isBreakEvenCalled = True
                    counter_obj.isProfitCheckPerformed = True

                if trade_bot_obj.isBreakEvenCalled:
                    if trade_bot_obj.currency_price < trade_bot_obj.place_order_price - (
                            trade_bot_obj.place_order_price * 0.0015):
                        trade_bot_obj.trailing_stop_loss_order(
                            stop_loss_price=(
                                    trade_bot_obj.place_order_price - (trade_bot_obj.place_order_price * 0.001)),
                            SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                            Decimal_point_price=symb_obj.current_decimal_point_price, QNTY=symb_obj.current_QNTY)
                        trade_bot_obj.isBreakEvenCalled = False

                if trade_bot_obj.position_quantity(SYMBOL=symb_obj.current_symbol, client=symb_obj.client()) == 0:
                    symb_obj.client().cancel_all_open_orders(symb_obj.current_symbol)
                    if trade_bot_obj.ShortHit == "ShortHit" and trade_bot_obj.currency_price < trade_bot_obj.place_order_price:
                        trade_bot_obj.ShortHit = "ShortHitProfit"
                    elif trade_bot_obj.ShortHit == "ShortHit" and trade_bot_obj.currency_price > trade_bot_obj.place_order_price:
                        trade_bot_obj.ShortHit = "ShortHitLoss"
                    trade_bot_obj.isOrderInProgress = False
                    trade_bot_obj.isShortOrderInProgress = False
                    trade_bot_obj.isBreakEvenCalled = False
                    trade_bot_obj.order_sequence += 1
                    trade_bot_obj.update_data_set(trade_bot_obj.ShortHit, SYMBOL=symb_obj.current_symbol,
                                                  client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                    counter_obj.update_data_set_tickers(side="sell", SYMBOL=symb_obj.current_symbol,
                                                        LongHit=trade_bot_obj.LongHit,
                                                        ShortHit=trade_bot_obj.ShortHit,
                                                        order_sequence=trade_bot_obj.order_sequence,
                                                        place_order_price=trade_bot_obj.place_order_price,
                                                        currency_price=trade_bot_obj.currency_price)
                    counter_obj.short_clear()
                    trade_bot_obj.ShortHit = "ShortHit"
                    trade_bot_obj.write_to_file(currentIndex=symb_obj.current_index)
                if indicator_obj.slow_speed_line > indicator_obj.fast_primary_trend_line:
                    print("Short Order In-Progress Cancelled Successfully")
                    trade_bot_obj.ShortHit = "ShortHitCrossing"
                    trade_bot_obj.isOrderInProgress = False
                    trade_bot_obj.isShortOrderInProgress = False
                    trade_bot_obj.isBreakEvenCalled = False
                    trade_bot_obj.cancel_executed_orders(SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                                                         QNTY=symb_obj.current_QNTY)
                    trade_bot_obj.order_sequence += 1
                    trade_bot_obj.update_data_set(trade_bot_obj.ShortHit, SYMBOL=symb_obj.current_symbol,
                                                  client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                    counter_obj.update_data_set_tickers(side="sell", SYMBOL=symb_obj.current_symbol,
                                                        LongHit=trade_bot_obj.LongHit,
                                                        ShortHit=trade_bot_obj.ShortHit,
                                                        order_sequence=trade_bot_obj.order_sequence,
                                                        place_order_price=trade_bot_obj.place_order_price,
                                                        currency_price=trade_bot_obj.currency_price)
                    counter_obj.short_clear()
                    trade_bot_obj.ShortHit = "ShortHit"
                    trade_bot_obj.write_to_file(currentIndex=symb_obj.current_index)
                if not trade_bot_obj.isOrderInProgress and not trade_bot_obj.isShortOrderInProgress:
                    print("Short Order Sleep Time is Called")
                    trade_bot_obj.update_data_set(side="sleep started", SYMBOL=symb_obj.current_symbol,
                                                  client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                    trade_bot_obj.time_dot_round(TIME_PERIOD)
                    trade_bot_obj.update_data_set(side="sleep ended", SYMBOL=symb_obj.current_symbol,
                                                  client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                    symb_obj.increment()
            elif not trade_bot_obj.isOrderInProgress and not trade_bot_obj.isOrderPlaced and len(symb_obj.symbols) > 17:
                print("\n--------- Currency ---------")
                print(symb_obj.current_symbol, ":", trade_bot_obj.currency_price)
                print("----------------------------")
                print("\n************** Strategy Result Getting Order Number ", trade_bot_obj.order_sequence,
                      " ***********", datetime.now(), "***********")
                if indicator_obj.slow_speed_line > indicator_obj.fast_primary_trend_line:
                    if indicator_obj.trend_line_1 >= indicator_obj.fast_primary_trend_line or indicator_obj.trend_line_2 >= indicator_obj.fast_primary_trend_line or indicator_obj.trend_line_3 >= indicator_obj.fast_primary_trend_line or indicator_obj.no_trend_zone_middle_line >= indicator_obj.fast_primary_trend_line:
                        print("Long Crossed But lines in between")
                    else:
                        print("Long Crossed looking for Hoffman Long signal wicked candle")
                        print("Hoffman Long Signal:", indicator_obj.long_signal_candle)
                        if indicator_obj.long_signal_candle:
                            trade_bot_obj.high_price = np.array(high)[-2]
                            trade_bot_obj.place_order_price = round(
                                trade_bot_obj.high_price + (trade_bot_obj.high_price * above_or_below_wick / 100),
                                symb_obj.current_decimal_point_price)
                            trade_bot_obj.trailing_order_price = trade_bot_obj.place_order_price
                            trade_bot_obj.stop_loss = ((
                                                               trade_bot_obj.place_order_price - indicator_obj.fast_primary_trend_line) / trade_bot_obj.place_order_price) * 100
                            trade_bot_obj.take_profit = trade_bot_obj.stop_loss * trade_bot_obj.profit_ratio
                            if trade_bot_obj.currency_price < trade_bot_obj.place_order_price:
                                trade_bot_obj.isOrderPlaced = True
                                trade_bot_obj.isLongOrderPlaced = True
                                trade_bot_obj.place_long_order(long=trade_bot_obj.place_order_price,
                                                               SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                                                               Decimal_point_price=symb_obj.current_decimal_point_price,
                                                               QNTY=symb_obj.current_QNTY)
                                trade_bot_obj.update_data_set(side="LongOrderPlaced", SYMBOL=symb_obj.current_symbol,
                                                              client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                                trade_bot_obj.write_to_file(currentIndex=symb_obj.current_index)
                                counter_obj.isProfitCheckPerformed = False
                            else:
                                print("Price is over the order price")
                else:
                    if indicator_obj.trend_line_1 <= indicator_obj.fast_primary_trend_line or indicator_obj.trend_line_2 <= indicator_obj.fast_primary_trend_line or indicator_obj.trend_line_3 <= indicator_obj.fast_primary_trend_line or indicator_obj.no_trend_zone_middle_line <= indicator_obj.fast_primary_trend_line:
                        print("Short Crossed But lines in between")
                    else:
                        print("Short Crossed looking for Hoffman Short signal wicked candle")
                        print("Hoffman Short Signal:", indicator_obj.short_signal_candle)
                        if indicator_obj.short_signal_candle:
                            trade_bot_obj.low_price = np.array(low)[-2]
                            trade_bot_obj.place_order_price = round(
                                trade_bot_obj.low_price - (trade_bot_obj.low_price * above_or_below_wick / 100),
                                symb_obj.current_decimal_point_price)
                            trade_bot_obj.trailing_order_price = trade_bot_obj.place_order_price
                            trade_bot_obj.stop_loss = (indicator_obj.fast_primary_trend_line - trade_bot_obj.place_order_price) / trade_bot_obj.place_order_price * 100
                            trade_bot_obj.take_profit = trade_bot_obj.stop_loss * trade_bot_obj.profit_ratio
                            if trade_bot_obj.currency_price > trade_bot_obj.place_order_price:
                                trade_bot_obj.isOrderPlaced = True
                                trade_bot_obj.isShortOrderPlaced = True
                                trade_bot_obj.place_short_order(short=trade_bot_obj.place_order_price,
                                                                SYMBOL=symb_obj.current_symbol, client=symb_obj.client(),
                                                                Decimal_point_price=symb_obj.current_decimal_point_price,
                                                                QNTY=symb_obj.current_QNTY)
                                trade_bot_obj.update_data_set(side="ShortOrderPlaced", SYMBOL=symb_obj.current_symbol,
                                                              client=symb_obj.client(), QNTY=symb_obj.current_QNTY)
                                trade_bot_obj.write_to_file(currentIndex=symb_obj.current_index)
                                counter_obj.isProfitCheckPerformed = False
                            else:
                                print("Price is over the order price")
                if not trade_bot_obj.isOrderPlaced:
                    symb_obj.increment()

        time.sleep(TIME_SLEEP)


if __name__ == "__main__":
    counters_obj = Counters()
    indicators_obj = Indicator()
    trading_bot_obj = TradingBot()
    symbol_obj = Symbols(current_index_symbol=0, current_index_time_frame=0)
    db = DB()
    while True:
        try:
            main(trading_bot_obj, counters_obj, indicators_obj, symbol_obj, db)
            # if os.path.exists(f'is_order_in_progress.txt'):
            #     file = open(f'is_order_in_progress.txt', 'r')
            #     x, y, z, xx, yy, zz, xxx, a, b, c, d, e, f, g, h = file.readlines()
            #     file.close()
            #     x = strip(x)
            #     y = strip(y)
            #     z = strip(z)
            #     xx = strip(xx)
            #     yy = strip(yy)
            #     zz = strip(zz)
            #     xxx = strip(xxx)
            #     a = strip(a)
            #     b = strip(b)
            #     c = strip(c)
            #     d = strip(d)
            #     e = strip(e)
            #     f = strip(f)
            #     g = strip(g)
            #     h = strip(h)
            #     if x == "True":
            #         trading_bot_obj.isOrderInProgress = True
            #     if y == "True":
            #         trading_bot_obj.isLongOrderInProgress = True
            #     if z == "True":
            #         trading_bot_obj.isShortOrderInProgress = True
            #     if xx == "True":
            #         trading_bot_obj.isOrderPlaced = True
            #     if yy == "True":
            #         trading_bot_obj.isLongOrderPlaced = True
            #     if zz == "True":
            #         trading_bot_obj.isShortOrderPlaced = True
            #     if xxx == "True":
            #         trading_bot_obj.newHoffmanSignalCheck = True
            #     trading_bot_obj.order_sequence = int(a)
            #     trading_bot_obj.high_price = float(b)
            #     trading_bot_obj.low_price = float(c)
            #     trading_bot_obj.place_order_price = float(d)
            #     trading_bot_obj.take_profit = float(e)
            #     trading_bot_obj.stop_loss = float(f)
            #     trading_bot_obj.trailing_order_price = float(g)
            #     symbol_obj.current_index = int(h)
            #     main(trading_bot_obj, counters_obj, indicators_obj, symbol_obj, db)
            # else:
            #     main(trading_bot_obj, counters_obj, indicators_obj, symbol_obj, db)
        except Exception as e:
            print(e)
            threads_exception_data(symbol="Main Thread", exception=e, order="null")
            try:
                time.sleep(20)
            except Exception as e:
                print(e)
                time.sleep(10)
