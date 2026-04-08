from __future__ import annotations

from pydantic import BaseModel, Field


class ProposalSummary(BaseModel):
    proposal_id: int
    title: str
    description: str
    amount: int
    recipient: str
    yes_votes: int = Field(default=0)
    no_votes: int = Field(default=0)
    quorum: int = Field(default=0)
    approval_bps: int = Field(default=5000)
    start_round: int = Field(default=0)
    end_round: int = Field(default=0)
    executed: bool = Field(default=False)
    closed: bool = Field(default=False)


class TreasuryBalance(BaseModel):
    address: str
    microalgos: int
