"""Backend pytest configuration.

Excludes non-test data directories from pytest collection so that
fixtures (acquired PDFs, generated manifests, uploads) are never
mistaken for test modules.

Note: ``collect_ignore_glob`` is honoured only during *default* discovery
(rootdir-relative). When a path is passed explicitly on the command line
(e.g. ``pytest scripts/archive``) the archive is still collectable on
demand, which is intentional — historical per-phase tests remain runnable
when explicitly requested.

Also sets ``pythonpath = ['.']`` so ``from app...`` imports resolve
from the backend root.
"""
from __future__ import annotations

collect_ignore_glob = [
    "ai_data/**",
    "uploads/**",
    "snapshots/**",
    "qdrant_storage/**",
    "storage_backup_before_qdrant_repair/**",
    "storage_corrupted_backup_20260818/**",
    "storage_corrupted_backup_20260818_final/**",
    "storage_corrupted_qdrant_1.12.4/**",
    "storage_old_corrupted/**",
    "scripts/archive/**",
    "venv/**",
]
