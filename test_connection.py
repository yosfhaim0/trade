import json
import ccxt


# ======================
# Load config
# ======================
with open("config_paper.json", "r") as f:
    cfg = json.load(f)

API_KEY = cfg["api_key"]
API_SECRET = cfg["api_secret"]
SYMBOL = cfg.get("symbol", "BTC/USDT")


# ======================
# Exchange
# ======================
exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True,
    "options": {
        "defaultType": "spot"
    }
})

# IMPORTANT: Testnet
exchange.set_sandbox_mode(True)


# ======================
# Account info
# ======================
account = exchange.private_get_account()

print("\n==============================")
print("BALANCES")
print("==============================")

for b in account["balances"]:
    free = float(b["free"])
    locked = float(b["locked"])
    if free > 0 or locked > 0:
        print(f"{b['asset']:6}  free={free:.6f}  locked={locked:.6f}")


print("\n==============================")
print("OPEN ORDERS")
print("==============================")

orders = exchange.fetch_open_orders(SYMBOL)
if not orders:
    print("No open orders")

for o in orders:
    print(
        f"{o['side']:4} "
        f"price={o['price']} "
        f"amount={o['amount']} "
        f"status={o['status']}"
    )


print("\n==============================")
print("TRADE HISTORY")
print("==============================")

trades = exchange.fetch_my_trades(SYMBOL, limit=20)

if not trades:
    print("No trades yet")

for t in trades:
    print(
        f"{t['side']:4} "
        f"price={t['price']} "
        f"amount={t['amount']} "
        f"time={t['datetime']}"
    )