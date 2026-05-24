"""Checkout-time import shim for the src-layout package.

The implementation lives in src/pfc_boundary_proof. This shim lets the public
README commands run directly from a fresh checkout with `python -m`.
"""

from __future__ import annotations

from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parent.parent / "src" / "pfc_boundary_proof"
if _SRC_PACKAGE.is_dir():
    __path__.append(str(_SRC_PACKAGE))

__version__ = "0.1.0"
