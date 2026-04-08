from __future__ import annotations

from app.algorand import clients


def get_algod_client():
    return clients.algod


def get_indexer_client():
    return clients.indexer
