from ib_insync import *
from datetime import datetime

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)


def is_monthly_exp(exp_date: datetime.date) -> bool:
    return exp_date.weekday() == 4 and 15 <= exp_date.day <= 21


def get_valid_expirations(stock, min_days=30, max_days=60):
    chains = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
    chain = chains[0]
    today = datetime.now().date()

    valid = []
    for exp in chain.expirations:
        exp_date = datetime.strptime(exp, "%Y-%m-%d").date() if "-" in exp else datetime.strptime(exp, "%Y%m%d").date()
        if min_days <= (exp_date - today).days <= max_days and is_monthly_exp(exp_date):
            valid.append(exp_date.strftime("%Y-%m-%d"))
    return sorted(valid)


def get_option_price(option: Option):
    try:
        ticker = ib.reqTickers(option)[0]
        return ticker.marketPrice(), abs(ticker.modelGreeks.delta or 0.0)
    except Exception as e:
        print(f"⚠️ Failed to get price for {option.symbol} {option.lastTradeDateOrContractMonth} {option.strike} {option.right}: {e}")
        return None, None


def create_spread(stock_symbol, exp_date, spread_type, strike1, strike2):
    call_or_put = 'C' if 'call' in spread_type else 'P'
    buy_strike, sell_strike = (strike1, strike2) if 'bull' in spread_type else (strike2, strike1)

    formatted_exp = exp_date.replace('-', '')  # convert to 'YYYYMMDD' format
    leg_buy = Option(stock_symbol, formatted_exp, buy_strike, call_or_put, 'SMART')
    leg_sell = Option(stock_symbol, formatted_exp, sell_strike, call_or_put, 'SMART')
    ib.qualifyContracts(leg_buy, leg_sell)

    if not leg_buy.lastTradeDateOrContractMonth or not leg_sell.lastTradeDateOrContractMonth:
        print(f"⚠️ Invalid contract fields for {stock_symbol} {exp_date} {strike1}-{strike2}")
        return None

    price_buy, _ = get_option_price(leg_buy)
    price_sell, delta_sell = get_option_price(leg_sell)

    if price_buy is None or price_sell is None:
        return None

    credit = price_sell - price_buy if 'bear' in spread_type else price_buy - price_sell
    width = abs(strike2 - strike1)
    max_profit = credit if 'bear' in spread_type else width - credit
    max_loss = width - credit if 'bear' in spread_type else credit
    pop = (1 - delta_sell) * 100

    return {
        'spread': spread_type,
        'buy': buy_strike,
        'sell': sell_strike,
        'credit/debit': credit,
        'max_profit': max_profit,
        'max_loss': max_loss,
        'POP': round(pop, 2),
        'expiration': exp_date
    }


def scan_spreads(symbols, strategies, min_strike=None, max_strike=None, target_credit=None):
    results = []
    for symbol in symbols:
        stock = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(stock)
        expirations = get_valid_expirations(stock)
        if not expirations:
            print(f"⚠️ No valid expirations found for {symbol}")
            continue
        exp_date = expirations[0]

        try:
            chain_data = ib.reqSecDefOptParams(symbol, '', 'STK', stock.conId)
            strikes = sorted(set(x for x in chain_data[0].strikes if x is not None))
        except Exception as e:
            print(f"⚠️ Failed to retrieve strikes for {symbol}: {e}")
            continue

        for spread_type in strategies:
            for i in range(len(strikes) - 1):
                s1, s2 = strikes[i], strikes[i + 1]
                if min_strike and (s1 < min_strike or s2 < min_strike):
                    continue
                if max_strike and (s1 > max_strike or s2 > max_strike):
                    continue
                try:
                    data = create_spread(symbol, exp_date, spread_type, s1, s2)
                    if data and (target_credit is None or data['credit/debit'] >= target_credit):
                        results.append({'symbol': symbol, **data})
                except Exception as e:
                    print(f"⚠️ Error generating spread for {symbol} {spread_type} {s1}-{s2}: {e}")
                    continue
    return results


# # דוגמה לשימוש:
# symbols = ['AAPL', 'MSFT']
# strategies = ['bull_call', 'bear_call', 'bull_put', 'bear_put']
# spreads = scan_spreads(symbols, strategies, min_strike=150, max_strike=300, target_credit=0.5)
#
# # תצוגה טבלאית ושמירה
# if spreads:
#     df = pd.DataFrame(spreads)
#     print(df.to_string(index=False))
#     df.to_csv("spreads_output.csv", index=False)
# else:
#     print("⚠️ No spreads found that match criteria.")
#
# ib.disconnect()
