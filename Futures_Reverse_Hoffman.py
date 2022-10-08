from datetime import datetime
import time
import threading
from Classes.Counters import Counters
from Classes.DB import DB, threads_exception_data
from Classes.Indicator import Indicator
from Classes.Symbols import Symbols
from Classes.TradingBot import TradingBot
from Config.Settings import TIME_PERIOD, TIME_SLEEP
from Dictionary.Strings import null_order, main_exception_1, main_exception_2
from Functions.Check_Order import check_order
from Functions.Mappers import assign_trade_bot_main_open
from Functions.Randoms import allow_thread, print_order_in_progress
from Functions.Threads.Short_Thread import short_order_placed
from Functions.Threads.Long_Thread import long_order_placed


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
            cancel_all_orders = threading.Thread(name="cancel_all_orders", target=symb_obj.cancel_all_orders,
                                                 args=("fake_argument1", "fake_argument1", "fake_argument1"))
            cancel_all_orders.start()
            symb_obj.reset_increment_to_specific_symbol(symbol=trade_bot_obj.order_executed_for_symbol)
            executed_order_on_body_check = threading.Thread(name="executed_order_on_body_check",
                                                            target=trade_bot_obj.executed_order_on_body_check,
                                                            args=(symb_obj.current_symbol, symb_obj.client(),
                                                                  symb_obj.current_QNTY))
            executed_order_on_body_check.start()
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
            # After Order Place Start Threads To Track Execution
            if trade_bot_obj.isOrderPlaced and trade_bot_obj.isLongOrderPlaced:

                placed_order_execution_check = threading.Thread(name=symb_obj.current_symbol,
                                                                target=long_order_placed,
                                                                args=(trade_bot_obj, indicator_obj,
                                                                      symb_obj, symb_obj.current_symbol,
                                                                      symb_obj.current_decimal_point_price,
                                                                      symb_obj.current_QNTY, symb_obj.current_index,
                                                                      symb_obj.client(), False))
                placed_order_execution_check.start()
                time.sleep(TIME_SLEEP)
                trade_bot_obj.isOrderPlaced = False
                trade_bot_obj.isLongOrderPlaced = False
                symb_obj.move_symbols()

            elif trade_bot_obj.isOrderPlaced and trade_bot_obj.isShortOrderPlaced:

                placed_order_execution_check = threading.Thread(name=symb_obj.current_symbol,
                                                                target=short_order_placed,
                                                                args=(trade_bot_obj, indicator_obj,
                                                                      symb_obj, symb_obj.current_symbol,
                                                                      symb_obj.current_decimal_point_price,
                                                                      symb_obj.current_QNTY, symb_obj.current_index,
                                                                      symb_obj.client(), False))
                placed_order_execution_check.start()
                time.sleep(TIME_SLEEP)
                trade_bot_obj.isOrderPlaced = False
                trade_bot_obj.isShortOrderPlaced = False
                symb_obj.move_symbols()

            elif trade_bot_obj.isOrderInProgress and trade_bot_obj.isLongOrderInProgress:
                counter_obj.calculate(currency_price=trade_bot_obj.currency_price,
                                      place_order_price=trade_bot_obj.place_order_price, side="buy")

                print_order_in_progress(current_symbol=symb_obj.current_symbol,
                                        currency_price=trade_bot_obj.currency_price,
                                        place_order_price=trade_bot_obj.place_order_price,
                                        take_profit=trade_bot_obj.take_profit,
                                        stop_loss=trade_bot_obj.stop_loss, side="buy")

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
                if indicator_obj.slow_speed_line > indicator_obj.fast_primary_trend_line:
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
                counter_obj.calculate(currency_price=trade_bot_obj.currency_price,
                                      place_order_price=trade_bot_obj.place_order_price, side="sell")

                print_order_in_progress(current_symbol=symb_obj.current_symbol,
                                        currency_price=trade_bot_obj.currency_price,
                                        place_order_price=trade_bot_obj.place_order_price,
                                        take_profit=trade_bot_obj.take_profit,
                                        stop_loss=trade_bot_obj.stop_loss, side="sell")

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
                if indicator_obj.slow_speed_line < indicator_obj.fast_primary_trend_line:
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

            # First Check Function to Place Orders
            elif not trade_bot_obj.isOrderInProgress and not trade_bot_obj.isOrderPlaced and len(symb_obj.symbols) > 17:
                check_order(trade_bot_obj=trade_bot_obj, symbol_obj=symb_obj, indicator_obj=indicator_obj,
                            counter_obj=counter_obj, open_price=open_price, high=high, low=low, close=close)
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
        except Exception as e:
            print(e)
            threads_exception_data(symbol=main_exception_1, exception=e, order=null_order)
            try:
                time.sleep(20)
            except Exception as e:
                print(e)
                threads_exception_data(symbol=main_exception_2, exception=e, order=null_order)
                time.sleep(10)
