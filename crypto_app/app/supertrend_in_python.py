import ccxt
import pandas as pd
from crypto_app.config_ccxt import config
import schedule
import time
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")


import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_supertrend(df):
    import matplotlib
    matplotlib.use('TkAgg')

    plt.style.use("seaborn-v0_8-darkgrid")

    fig, ax = plt.subplots(figsize=(16, 8), dpi=150)

    ax.plot(df["timestamp"], df["close"], label="Close Price", color="#1f77b4", linewidth=2)

    # SuperTrend лінії
    ax.plot(df["timestamp"], df["upperband"], label="Upper Band", color="#d62728", linestyle="--", linewidth=1.5)
    ax.plot(df["timestamp"], df["lowerband"], label="Lower Band", color="#2ca02c", linestyle="--", linewidth=1.5)

    for i in range(1, len(df)):
        color = 'green' if df["in_uptrend"][i] else 'red'
        ax.axvspan(df["timestamp"][i - 1], df["timestamp"][i], color=color, alpha=0.05)

    for i in range(1, len(df)):
        prev = df["in_uptrend"][i - 1]
        curr = df["in_uptrend"][i]
        if not prev and curr:
            ax.scatter(df["timestamp"][i], df["close"][i], color="lime", marker="^", s=100, label="Buy" if i == 1 else "")
        elif prev and not curr:
            ax.scatter(df["timestamp"][i], df["close"][i], color="red", marker="v", s=100, label="Sell" if i == 1 else "")

    ax.set_title("SuperTrend Strategy (ETH/USDT)", fontsize=18, fontweight="bold")
    ax.set_xlabel("Time", fontsize=14)
    ax.set_ylabel("Price (USDT)", fontsize=14)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc="upper left", fontsize=12)

    plt.tight_layout()
    plt.show()



pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.max_rows", None)

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



def tr(df):
    df["prefios_close"] = df["close"].shift(1)
    df["high - low"] = df["high"] - df["low"]
    df["high - pc"] = abs(df["high"] - df["prefios_close"])
    df["low - pc"] = abs(df["low"] - df["prefios_close"])
    tr = df[["high - low", "high - pc", "low - pc"]].max(axis=1)

    return tr

def atr(df, period=14):
    df["tr"] = tr(df)
    the_atr = df["tr"].rolling(period).mean()

    return the_atr
    # df["atr"] = the_atr

def supertrand(df, period=7, multi_param=3):
    print("SuperTrand!")
    hlt2 = ((df["high"] + df["low"]) / 2)
    df["atr"] = atr(df, period)
    df["upperband"] = hlt2 + (multi_param * df["atr"])
    df["lowerband"] = hlt2 - (multi_param * df["atr"])
    df["in_uptrend"] = True

    for current in range(1, len(df.index)):
        previous = current - 1
        if df.loc[current, "close"] > df.loc[previous, "upperband"]:
            df.loc[current, "in_uptrend"] = True

        elif df.loc[current, "close"] < df.loc[previous, "lowerband"]:
            df.loc[current, "in_uptrend"] = False

        else:
            df.loc[current, "in_uptrend"] = df.loc[previous, "in_uptrend"]

            if df.loc[current, "in_uptrend"] and df.loc[current, "lowerband"] < df.loc[previous, "lowerband"]:
                df.loc[current, "lowerband"] = df.loc[previous, "lowerband"]

            if not df.loc[current, "in_uptrend"] and df.loc[current, "upperband"] > df.loc[previous, "upperband"]:
                df.loc[current, "upperband"] = df.loc[previous, "upperband"]

    return df

def check_by_sell_signal(df):
    in_position = False
    print("checkin for buy and sell")
    print(df.tail(5))

    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1
    if not df["in_uptrend"][previous_row_index] and df["in_uptrend"][last_row_index]:
        if not in_position:
            print("Change to uptrend: Buy!")
            # order = exchange.create_market_buy_order("ETH/USDT", 0.0001)

            in_position = True
        else:
            print("Already in position, nothing to do")

    if df["in_uptrend"][previous_row_index] and not df["in_uptrend"][last_row_index]:
        if in_position:
            print("Change to downbend: Sell!")
            # order_sell = exchange.create_market_sell_order("ETH/USDT", 0.0001)

            in_position = False
        else:
            print("You aren`t in position")


def fetch_bars():
    print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv("ETH/USDT", timeframe="1m", limit=100)

    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    super_trend = supertrand(df)

    # print(super_trend)

    check_by_sell_signal(super_trend)

schedule.every(2).seconds.do(fetch_bars)


while True:
    schedule.run_pending()
    time.sleep(1)

# print(df)


# basic upper band = (()high + low)/ 2) + (multiplier * atr)
# basic lower band = (()high + low)/ 2) - (multiplier * atr)







