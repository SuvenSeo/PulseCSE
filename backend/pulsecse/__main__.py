from __future__ import annotations

import argparse
import json
import threading

from pulsecse.api.app import get_service
from pulsecse.bot.commands import CommandRouter
from pulsecse.bot.telegram_runtime import TelegramBotRuntime
from pulsecse.config import settings
from pulsecse.migrate import run_migrations
from pulsecse.observability import configure_logging
from pulsecse.poller import Poller


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(prog="pulsecse", description="PulseCSE Pro backend")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("migrate", help="Apply SQL migrations or initialize SQLite schema")
    sub.add_parser("seed", help="Initialize database with demo stocks, portfolio, watchlist, and rules")
    tick = sub.add_parser("tick", help="Run one market tick and evaluate alerts")
    tick.add_argument("--force", action="store_true", help="Ignore market-hours guard")
    worker = sub.add_parser("poller", help="Run market-hours polling worker")
    worker.add_argument("--interval", type=int, default=settings.poll_interval_seconds)
    worker.add_argument("--force", action="store_true", help="Poll outside market hours")
    sub.add_parser("worker", help="Alias for poller")
    sub.add_parser("bot", help="Run Telegram long-polling bot")
    sub.add_parser("both", help="Run bot startup check, then poller in same process")
    cmd = sub.add_parser("command", help="Run one bot command from the CLI")
    cmd.add_argument("text", nargs="+")
    sim = sub.add_parser("simulate", help="Run a deterministic scenario")
    sim.add_argument("scenario", choices=["jkh_breakout", "hnb_support_break", "comb_disclosure", "dial_volume", "market_rally"])
    api = sub.add_parser("api", help="Run FastAPI app with uvicorn")
    api.add_argument("--host", default=settings.host)
    api.add_argument("--port", type=int, default=settings.port)
    args = parser.parse_args()

    if args.command == "migrate":
        ran = run_migrations()
        print(json.dumps({"applied": ran, "count": len(ran)}, indent=2))
        return

    service = get_service()

    if args.command == "seed":
        service.bootstrap()
        print("PulseCSE database initialized.")
    elif args.command == "tick":
        print(json.dumps(service.tick(force=args.force).to_dict(), indent=2))
    elif args.command in {"poller", "worker"}:
        interval = getattr(args, "interval", settings.poll_interval_seconds)
        force = getattr(args, "force", False)
        Poller(service, interval_seconds=interval, respect_market_hours=not force).run_forever()
    elif args.command == "simulate":
        print(json.dumps(service.simulate(args.scenario).to_dict(), indent=2))
    elif args.command == "command":
        result = CommandRouter(service.repository).handle(" ".join(args.text), settings.default_user_id)
        print(result.text)
    elif args.command == "bot":
        TelegramBotRuntime(CommandRouter(service.repository)).run(drop_pending_updates=True)
    elif args.command == "both":
        poller = Poller(service, interval_seconds=settings.poll_interval_seconds, respect_market_hours=True)
        if settings.telegram_token:
            thread = threading.Thread(target=poller.run_forever, daemon=True)
            thread.start()
            TelegramBotRuntime(CommandRouter(service.repository)).run(drop_pending_updates=True)
        else:
            print("No Telegram token configured; running poller only. Set PULSECSE_TELEGRAM_TOKEN for bot+poller mode.")
            poller.run_forever()
    elif args.command == "api":
        import uvicorn
        uvicorn.run("pulsecse.api.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
