from __future__ import annotations

import argparse
import json
import time

from pulsecse.api.app import create_app, get_service
from pulsecse.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(prog="pulsecse", description="PulseCSE Pro backend")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed", help="Initialize database with demo stocks, watchlist, and rules")
    sub.add_parser("tick", help="Run one market tick and evaluate alerts")
    worker = sub.add_parser("worker", help="Run continuous polling worker")
    worker.add_argument("--interval", type=int, default=60)
    sim = sub.add_parser("simulate", help="Run a deterministic scenario")
    sim.add_argument("scenario", choices=["jkh_breakout", "hnb_support_break", "comb_disclosure", "dial_volume", "market_rally"])
    api = sub.add_parser("api", help="Run FastAPI app with uvicorn")
    api.add_argument("--host", default=settings.host)
    api.add_argument("--port", type=int, default=settings.port)
    args = parser.parse_args()

    service = get_service()

    if args.command == "seed":
        service.bootstrap()
        print("PulseCSE database initialized.")
    elif args.command == "tick":
        print(json.dumps(service.tick().to_dict(), indent=2))
    elif args.command == "simulate":
        print(json.dumps(service.simulate(args.scenario).to_dict(), indent=2))
    elif args.command == "worker":
        print(f"PulseCSE worker running every {args.interval}s. Ctrl+C to stop.")
        while True:
            result = service.tick()
            print(f"tick snapshots={len(result.snapshots)} disclosures={len(result.disclosures)} events={len(result.events)}")
            time.sleep(args.interval)
    elif args.command == "api":
        import uvicorn

        uvicorn.run("pulsecse.api.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
