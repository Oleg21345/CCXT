import ccxt
from crypto_app.config_ccxt import config


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


balance = exchange.fetch_balance()

print(balance["total"]["USDT"])

# order = exchange.create_mark_buy_order("USDT/BTN")
# print(order)


