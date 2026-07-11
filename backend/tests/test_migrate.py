from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class MigrationTests(unittest.TestCase):
    def test_sqlite_migrations_marked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "migrate.sqlite3"
            with mock.patch.dict(os.environ, {"PULSECSE_DATABASE": f"sqlite:///{db}"}):
                import importlib
                import pulsecse.config as cfg
                import pulsecse.migrate as migrate
                import pulsecse.storage.factory as factory
                importlib.reload(cfg)
                importlib.reload(factory)
                importlib.reload(migrate)
                ran = migrate.run_migrations()
                self.assertGreaterEqual(len(ran), 1)


if __name__ == "__main__":
    unittest.main()
