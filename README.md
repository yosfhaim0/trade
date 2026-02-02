# Crypto Trading Bot (Swing Strategy)

This project provides a modular crypto trading bot built around:

- **Exchange abstraction** (live vs. paper account is purely config).
- **Strategy layer** (easy to swap or extend).
- **Trading engine** (orchestrates data, decisions, orders).
- **Reporting** (status + trades for online visibility).

## Quick start

```bash
python -m tradebot.main --config config_paper.json --once
```

To run continuously:

```bash
python -m tradebot.main --config config_paper.json
```

## Online results

Reports are written to `reports/`:

- `status.json` – latest signal and price snapshot.
- `trades.csv` – executed trades.

You can serve them remotely:

```bash
python -m tradebot.server --reports-dir reports --port 8000
```

## Config

`config_paper.json` can include:

```json
{
  "api_key": "...",
  "api_secret": "...",
  "sandbox": true,
  "symbol": "BTC/USDT",
  "timeframe": "1d",
  "short_ema": 5,
  "long_ema": 20,
  "risk_fraction": 0.1,
  "poll_interval_seconds": 3600,
  "reports_dir": "reports"
}
```

The same schema works for live trading by setting `sandbox: false` in `config.json`.
