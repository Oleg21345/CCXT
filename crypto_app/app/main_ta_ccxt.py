import ta
from ta.volatility import BollingerBands, AverageTrueRange
import ccxt
from crypto_app.config_ccxt import config
import pandas as pd

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_SECRET_KEY,
    'timeout': 30000,
})

exchange.load_time_difference()

data = exchange.load_markets()

bars = exchange.fetch_ohlcv("ETH/USDT", limit=40)

df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])

bb_indicetor = BollingerBands(df["close"], window=20, window_dev=2)


df["upper_band"] = bb_indicetor.bollinger_hband()
df["lower_band"] = bb_indicetor.bollinger_lband()
df["movieng_band"] = bb_indicetor.bollinger_mavg()


atr_indicetor = AverageTrueRange(df['high'], df['low'], df['close'])

df["atr"] = atr_indicetor.average_true_range()

df = df.dropna()

print(df)

