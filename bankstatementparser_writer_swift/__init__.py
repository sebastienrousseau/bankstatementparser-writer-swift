# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""SWIFT MT940 & MT942 statement exporter for bankstatementparser."""

from __future__ import annotations

from .writer import to_mt940, to_mt942, write_mt940, write_mt942

__version__ = "0.0.19"
__all__ = [
    "__version__",
    "to_mt940",
    "to_mt942",
    "write_mt940",
    "write_mt942",
]
