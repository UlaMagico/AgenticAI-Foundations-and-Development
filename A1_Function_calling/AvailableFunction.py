EXCHANGE_RATE_DICT = {
    "USD_TWD": "32.0",
    "JPY_TWD": "0.2",
    "EUR_USD": "1.2"
}

STOCK_PRICE_DICT = {
    "AAPL": "260.00",
    "TSLA": "430.00",
    "NVDA": "190.00"
}

def get_exchange_rate(currency_pair: str):
    if currency_pair in EXCHANGE_RATE_DICT:
        return {
            "currency_pair": currency_pair,
            "rate": EXCHANGE_RATE_DICT[currency_pair]
        }
    else: return {"error": "Data not found"}

def get_stock_price(symbol: str):
    if symbol in STOCK_PRICE_DICT:
        return {
            "symbol": symbol,
            "rate": STOCK_PRICE_DICT[symbol]
        }
    else: return {"error": "Data not found"}