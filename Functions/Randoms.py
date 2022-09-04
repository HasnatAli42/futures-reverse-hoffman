def allow_thread(t_obj: TradingBot):
    time.sleep(TIME_SLEEP*4)
    t_obj.isThreadAllowed = True