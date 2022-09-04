from Classes.TradingBot import TradingBot
from Classes.Indicator import Indicator


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