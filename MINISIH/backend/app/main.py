from __future__ import annotations

import base64

from fastapi import FastAPI, HTTPException
from algosdk.encoding import encode_address

from app.algorand import app_address, clients, read_box_bytes
from app.schemas import ProposalSummary, TreasuryBalance
from app.settings import settings

app = FastAPI(title="DAO Treasury Voting Wallet API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "network": settings.network}


@app.get("/treasury/balance", response_model=TreasuryBalance)
def treasury_balance() -> TreasuryBalance:
    if settings.app_id <= 0:
        raise HTTPException(status_code=400, detail="APP_ID is not configured")
    account = clients.algod.account_info(app_address())
    return TreasuryBalance(address=account["address"], microalgos=account["amount"])


def _decode_uint(data: bytes | None) -> int:
    if not data:
        return 0
    return int.from_bytes(data, byteorder="big")


def _decode_text(data: bytes | None) -> str:
    if not data:
        return ""
    return data.decode("utf-8")


def _decode_address(data: bytes | None) -> str:
    if not data:
        return ""
    if len(data) == 32:
        return encode_address(data)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return ""


def _proposal_from_boxes(proposal_id: int) -> ProposalSummary | None:
    title = _decode_text(read_box_bytes(f"p:{proposal_id}:title"))
    description = _decode_text(read_box_bytes(f"p:{proposal_id}:description"))
    amount = _decode_uint(read_box_bytes(f"p:{proposal_id}:amount"))
    recipient = _decode_address(read_box_bytes(f"p:{proposal_id}:recipient"))

    if not title and not description and amount == 0 and not recipient:
        return None

    return ProposalSummary(
        proposal_id=proposal_id,
        title=title,
        description=description,
        amount=amount,
        recipient=recipient,
        yes_votes=_decode_uint(read_box_bytes(f"p:{proposal_id}:yes")),
        no_votes=_decode_uint(read_box_bytes(f"p:{proposal_id}:no")),
        quorum=_decode_uint(read_box_bytes(f"p:{proposal_id}:quorum")),
        approval_bps=_decode_uint(read_box_bytes(f"p:{proposal_id}:approval")),
        start_round=_decode_uint(read_box_bytes(f"p:{proposal_id}:start")),
        end_round=_decode_uint(read_box_bytes(f"p:{proposal_id}:end")),
        executed=_decode_uint(read_box_bytes(f"p:{proposal_id}:executed")) == 1,
        closed=_decode_uint(read_box_bytes(f"p:{proposal_id}:closed")) == 1,
    )


def _global_uint(key: str) -> int:
    if settings.app_id <= 0:
        return 0
    application = clients.algod.application_info(settings.app_id)
    for item in application.get("params", {}).get("global-state", []):
        encoded_key = item.get("key", "")
        if encoded_key and base64.b64decode(encoded_key).decode("utf-8") == key:
            value = item.get("value", {})
            return int(value.get("uint", 0))
    return 0


@app.get("/proposals", response_model=list[ProposalSummary])
def list_proposals() -> list[ProposalSummary]:
    if settings.app_id <= 0:
        return []
    max_id = _global_uint("next_id")
    if max_id <= 1:
        return []

    proposals: list[ProposalSummary] = []
    for proposal_id in range(1, max_id):
        proposal = _proposal_from_boxes(proposal_id)
        if proposal is not None:
            proposals.append(proposal)
    return proposals


@app.get("/proposals/{proposal_id}", response_model=ProposalSummary)
def get_proposal(proposal_id: int) -> ProposalSummary:
    proposal = _proposal_from_boxes(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal
