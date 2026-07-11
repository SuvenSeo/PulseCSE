# PulseCSE Pro Runbook

## Local backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[api]
python -m pulsecse seed
python -m pulsecse api
```

Open `http://127.0.0.1:8088/live.html`.

## Run a market tick

```bash
python -m pulsecse tick
```

## Run a scenario

```bash
python -m pulsecse simulate jkh_breakout
python -m pulsecse simulate hnb_support_break
python -m pulsecse simulate comb_disclosure
python -m pulsecse simulate dial_volume
python -m pulsecse simulate market_rally
```

## Worker mode

```bash
python -m pulsecse worker --interval 60
```

## Full check

```bash
npm run fullcheck
```

## Reset local database

Delete `data/pulsecse.sqlite3`, then run:

```bash
python -m pulsecse seed
```

## Docker

```bash
docker compose up --build
```
