#!/usr/bin/python3
"""Thin shim so the app can be run from a raw git checkout.

The real entry point lives in ``sosdesktop.main:main`` (also exposed as the
``sos-desktop`` console script via pyproject). This shim just ensures the
project root is importable, then delegates.
"""
import os
import sys

# Ensure project root is on sys.path so 'sosdesktop' can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sosdesktop.main import main  # noqa: E402

if __name__ == "__main__":
    main()
