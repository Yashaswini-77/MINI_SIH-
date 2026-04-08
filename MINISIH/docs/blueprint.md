# DAO Treasury Voting Wallet Blueprint

## 1. System Architecture

```text
React Frontend
  -> Wallet signing in browser (Pera Wallet / AlgoSigner)
  -> Optional FastAPI backend for reads and analytics
  -> Algorand smart contract
  -> Treasury held by the application account
```

### Why Algorand

- Fast finality and low transaction fees.
- Deterministic smart contracts with inner transactions.
- Box storage is a natural fit for proposal metadata and per-wallet vote markers.
- Simple wallet integration for demo environments.

### Smart Contract vs Backend

- Smart contract: proposal creation, one-vote-per-wallet enforcement, quorum checks, execution, and treasury release.
- Backend: proposal listing, search, pagination, caching, analytics, and dashboard aggregation only.
- Wallet: signs all governance transactions locally; backend never signs treasury movement.

## 2. Smart Contract Design

### Global State

- `admin`: contract creator / DAO operator.
- `next_id`: next proposal id.
- `default_quorum`: fallback quorum.
- `default_approval_bps`: default approval threshold.
- `proposal_lifetime`: default voting duration.

### Box Layout

Proposal metadata boxes:

- `p:{id}:title`
- `p:{id}:description`
- `p:{id}:amount`
- `p:{id}:recipient`
- `p:{id}:creator`
- `p:{id}:start`
- `p:{id}:end`
- `p:{id}:quorum`
- `p:{id}:approval`
- `p:{id}:yes`
- `p:{id}:no`
- `p:{id}:executed`
- `p:{id}:closed`

Vote marker boxes:

- `v:{id}:{wallet}` -> existence means the wallet already voted.

### Contract Methods

- `create_proposal`
- `vote`
- `execute`
- `close_failed`

### Governance Rules

- One vote per wallet per proposal.
- Voting is blocked after the deadline.
- Execution is blocked before the deadline.
- Funds are released only by an inner transaction from the application account.
- Proposal metadata is immutable after creation.

## 3. Frontend Plan

### Pages / Sections

- Dashboard with proposal list and treasury balance.
- Create Proposal form.
- Vote UI with yes/no actions and current totals.
- Proposal detail panel.

### Wallet Flow

- Connect Pera Wallet or AlgoSigner.
- Build application call transaction in the browser.
- Ask wallet to sign.
- Send signed transaction to algod.
- Refresh chain state after confirmation.

## 4. Optional Backend

### Read APIs

- `GET /health`
- `GET /treasury/balance`
- `GET /proposals`
- `GET /proposals/{proposal_id}`

### Off-chain Only

- Pagination
- Search
- Analytics
- Cached proposal views
- Notification hooks

## 5. Transaction Flow

### Create Proposal

1. User fills the form.
2. Frontend builds an application call with metadata arguments.
3. Wallet signs locally.
4. Contract writes proposal data into boxes.

### Vote

1. User selects yes or no.
2. Frontend checks whether the wallet has already voted.
3. Wallet signs the vote app call.
4. Contract stores a vote marker and updates counts.

### Execute

1. Proposal reaches deadline.
2. Anyone can call execute.
3. Contract checks quorum and approval threshold.
4. Inner payment releases treasury funds.

## 6. Security

- Replay resistance comes from transaction validity windows and on-chain state checks.
- Double voting is blocked by vote marker boxes.
- Unauthorized withdrawals are impossible because only the app can issue the payment.
- Expired proposals are finalized without payout.

## 7. Deployment

### Compile

```bash
cd <repo-root>
python -m pip install -r contracts/requirements.txt
python -m scripts.compile_contract
```

### Testnet

1. Fund a testnet deployer account.
2. Compile approval and clear TEAL.
3. Create the application.
4. Fund the application address.
5. Configure `APP_ID` in backend and frontend env files.

### Run

```bash
cd backend
uvicorn app.main:app --reload --port 8000

cd frontend
npm install
npm run dev
```

## 8. Hackathon Extensions

- Delegated voting.
- Token-weighted voting.
- Governance NFT membership.
- Live analytics dashboard.
- Execution history and proposal activity feed.
