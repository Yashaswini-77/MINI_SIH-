# DAO Treasury Voting Wallet

A repo-ready Algorand governance stack for small communities and hackathon demos.

## What is included

- PyTeal smart contract with proposal creation, voting, quorum checks, and treasury release.
- FastAPI read-only backend for proposal and treasury views.
- React + TypeScript frontend for wallet connection, proposal creation, voting, and dashboard views.
- Deployment and local development guidance.

## Architecture

- On-chain: proposal immutability, vote tracking, quorum enforcement, and treasury payment release.
- Off-chain: indexing, pagination, search, and analytics.
- Wallets: Pera Wallet or AlgoSigner sign all state-changing transactions locally.

## Repository layout

- `contracts/` PyTeal contract source.
- `backend/` FastAPI read layer.
- `frontend/` React application.
- `scripts/` utility scripts for compiling and deployment.

## Quick start

### 1. Smart contract

```bash
cd <repo-root>
python -m pip install -r requirements.txt
python -m scripts.compile_contract
```

The compile script writes TEAL output into `artifacts/`.

### 2. Backend

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

## Notes

- The backend is intentionally read-only.
- Treasury funds are released only by the smart contract inner transaction.
- Proposal metadata is immutable after creation.
- Vote uniqueness is enforced per wallet per proposal through box storage.

See `contracts/dao_treasury.py` and `frontend/src/App.tsx` for the core implementation points.
See `docs/blueprint.md` for the full architecture, data model, security notes, and deployment flow.
