#!/usr/bin/env bash
set -euo pipefail
npm run check
npm test
PYTHONPATH=backend python -m compileall -q backend
PYTHONPATH=backend python -m unittest discover -s backend/tests
