import sqlite3 as sl
from datetime import datetime


class DB:
    def __init__(self):
        self.DB = "SQLite"

    def initialize_db(self, SYMBOL):
        con = sl.connect('../orders-executed.db')
        with con:
            con.execute(f"""
                CREATE TABLE IF NOT EXISTS FUTURES_{SYMBOL}_HOFFMAN  (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    order_sequence TEXT,
                    Current_eth_price TEXT,
                    Etherium_quantity TEXT,
                    Remaining_quantity TEXT,
                    LeverageTaken TEXT,
                    TotalWalletBalance TEXT,
                    AvailableBalance TEXT,
                    OrderFee TEXT,
                    Method_applied TEXT,
                    Usd_used TEXT,
                    LowestPrice TEXT,
                    HighestPrice TEXT,
                    OrderPrice TEXT,
                    TakeProfitPrice TEXT,
                    StopLossPrice TEXT,
                    Time TEXT,
                    Order1 TEXT,
                    Order2 TEXT
                );
            """)

        con = sl.connect('../orders-executed.db')
        with con:
            con.execute(f"""
                CREATE TABLE IF NOT EXISTS FUTURES_{SYMBOL}_HOFFMAN_TICKERS (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    Order_sequence TEXT,
                    Symbol TEXT,
                    Order_type TEXT,
                    Start_price TEXT,
                    End_price TEXT,
                    Operation_type TEXT,
                    Total_Profit TEXT,
                    Total_Loss TEXT,
                    isValid TEXT,
                    Time TEXT,
                    Profit_Counter TEXT,
                    Loss_Counter TEXT,
                    Profit_First TEXT,
                    Loss_First TEXT
                );
            """)

        con = sl.connect('../orders-executed.db')
        with con:
            con.execute(f"""
                        CREATE TABLE IF NOT EXISTS FUTURES_{SYMBOL}_HOFFMAN_TRAILING_ORDERS (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            Symbol TEXT,
                            Order2 TEXT,
                            Time TEXT
                        );
                    """)

        con = sl.connect('../orders-executed.db')
        with con:
            con.execute(f"""
                                CREATE TABLE IF NOT EXISTS FUTURES_HOFFMAN_THREADS_EXCEPTION (
                                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    Symbol TEXT,
                                    Exception TEXT,
                                    CancelOrder TEXT,
                                    Time TEXT
                                );
                            """)

        con = sl.connect('../orders-executed.db')
        with con:
            con.execute(f"""
                                CREATE TABLE IF NOT EXISTS HARMONIC_PARTIAL_PATTERNS (
                                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    Harmonic TEXT,
                                    Time TEXT
                                );
                            """)

        con = sl.connect('../orders-executed.db')
        with con:
            con.execute(f"""
                                CREATE TABLE IF NOT EXISTS HARMONIC_COMPLETE_PATTERNS (
                                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    Harmonic TEXT,
                                    Time TEXT
                                );
                            """)

    def insert_harmonic_partial_pattern(self, String):
        con = sl.connect('../orders-executed.db')
        sql = f'INSERT INTO HARMONIC_PARTIAL_PATTERNS (Harmonic, Time) values(?,?) '
        data = [
            (str(String)), (str(datetime.now())),
        ]
        with con:
            con.execute(sql, data)
            con.commit()

    def insert_harmonic_complete_pattern(self, String):
        con = sl.connect('../orders-executed.db')
        sql = f'INSERT INTO HARMONIC_COMPLETE_PATTERNS (Harmonic, Time) values(?,?) '
        data = [
            (str(String)), (str(datetime.now())),
        ]
        with con:
            con.execute(sql, data)
            con.commit()


def threads_exception_data(symbol, exception, order):
    con = sl.connect('../orders-executed.db')
    sql = f'INSERT INTO FUTURES_HOFFMAN_THREADS_EXCEPTION (Symbol, Exception, CancelOrder, Time) values(?,?,?,?) '
    data = [
        (str(symbol)), (str(exception)), (str(order)), (str(datetime.now()))
    ]
    with con:
        con.execute(sql, data)
        con.commit()
