from __future__ import annotations

from pulsecse.bot.commands import CommandRouter
from pulsecse.config import settings
from pulsecse.observability import log_event


class TelegramBotRuntime:
    """Optional python-telegram-bot long-polling runtime.

    It mirrors Chime's Telegram-first workflow, but the command core remains
    transport-neutral so the same behavior works from CLI, API, Telegram, or tests.
    """

    def __init__(self, router: CommandRouter, token: str | None = None) -> None:
        self.router = router
        self.token = token or settings.telegram_token

    def run(self, drop_pending_updates: bool = True) -> None:
        if not self.token:
            raise RuntimeError("PULSECSE_TELEGRAM_TOKEN is required for bot mode")
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Telegram mode requires: pip install python-telegram-bot>=21") from exc

        async def handle(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
            if not update.message or not update.message.text:
                return
            user_id = str(update.effective_user.id if update.effective_user else settings.default_user_id)
            result = self.router.handle(update.message.text, user_id=user_id)
            await update.message.reply_text(result.text)

        app = Application.builder().token(self.token).build()
        for name in ["help", "watch", "unwatch", "watchlist", "mywatchlist", "alert", "alerts", "myalerts", "cancel", "portfolio", "holding", "events"]:
            app.add_handler(CommandHandler(name, handle))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
        log_event("telegram_bot_started", drop_pending_updates=drop_pending_updates)
        app.run_polling(drop_pending_updates=drop_pending_updates)
