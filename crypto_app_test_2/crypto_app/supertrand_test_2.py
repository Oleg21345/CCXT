import ccxt
import pandas as pd
from crypto_app.config_ccxt import config
import schedule
import time
from datetime import datetime
import warnings


pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.max_rows", None)
warnings.filterwarnings("ignore")

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_SECRET_KEY,
    'timeout': 30000,
    "enableRateLimit": True,
    "options": {
        "adjustForTimeDifference": True
    }
})

exchange.load_time_difference()


bars = exchange.fetch_ohlcv("ETH/USDT", timeframe="1m", limit=200)

df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")


def tr(df):
    df["previous_close"] = df["close"].shift(1)
    df["high-low"] = df["high"] - df["low"]
    df["high-pc"] = abs(df["high"] - df["previous_close"])
    df["low-pc"] = abs(df["low"] - df["previous_close"])
    tr = df[["high-low", "high-pc", "low-pc"]].max(axis=1)

    return tr

def atr(df):
    df["tr"] = tr(df)

    the_atr = df["tr"].rolling(5).mean()
    return the_atr

def supertrend(df, period=14, multiplier=3):
    df["atr"] = atr(df)
    hl2 = (df["high"] + df["low"])  / 2
    df["upperband"] = hl2 + (multiplier * df["atr"])
    df["lowerband"] = hl2 - (multiplier * df["atr"])
    df["in_uptrend"] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df.loc[current, "close"] > df.loc[previous,"upperband"]:
            df.loc[current, "in_uptrend"] = True

        elif df.loc[current, "close"] < df.loc[previous,"lowerband"]:
            df.loc[current, "in_uptrend"] = False

        else:
            df.loc[current, "in_uptrend"] = df.loc[previous, "in_uptrend"]

            if df.loc[current, "in_uptrend"] and df.loc[current, "lowerband"] < df.loc[previous, "lowerband"]:
                df.loc[current, "lowerband"] = df.loc[previous, "lowerband"]

            if not df.loc[current, "in_uptrend"] and df.loc[current, "upperband"] > df.loc[previous, "upperband"]:
                df.loc[current, "upperband"] = df.loc[previous, "upperband"]

    print(df)

supertrend(df)

















