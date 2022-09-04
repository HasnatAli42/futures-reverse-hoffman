from Config.Settings import above_or_below_wick
from Dictionary.Strings import long, short


def place_order_price(side, price, round_value):
    if side == short:
        return round(price + (price * above_or_below_wick / 100), round_value)
    elif side == long:
        return round(price - (price * above_or_below_wick / 100), round_value)


def calculate_stop_loss(side, price, indicator_value):
    if side == short:
        return ((price - indicator_value) / price) * 100
    elif side == long:
        return ((indicator_value - price) / price) * 100


