from __future__ import annotations

import base64
from dataclasses import dataclass

from algosdk.logic import get_application_address
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from app.settings import settings


@dataclass
class AlgorandClients:
    algod: AlgodClient
    indexer: IndexerClient


clients = AlgorandClients(
    algod=AlgodClient(settings.algod_token, settings.algod_address),
    indexer=IndexerClient(settings.indexer_token, settings.indexer_address),
)


def app_address() -> str:
    if settings.app_id <= 0:
        return ""
    return get_application_address(settings.app_id)


def read_box_bytes(box_name: str) -> bytes | None:
    if settings.app_id <= 0:
        return None
    try:
        response = clients.algod.application_box_by_name(settings.app_id, box_name.encode())
        value = response.get("value")
        if value is None:
            return None
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return base64.b64decode(value)
        return base64.b64decode(value)
    except Exception:
        return None
