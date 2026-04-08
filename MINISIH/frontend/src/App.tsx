import { useMemo, useState } from 'react';
import { ProposalCard } from './components/ProposalCard';
import { APP_ID, formatAlgo, getAppAddress, getSuggestedParams } from './lib/algorand';
import { connectWallet } from './lib/wallet';
import type { Proposal, WalletName } from './types';

const seedProposals: Proposal[] = [
  {
    id: 1,
    title: 'Club event funding',
    description: 'Sponsor room booking and refreshments for the semester kickoff.',
    amount: 1500000,
    recipient: 'RECIPIENT-ADDRESS-PLACEHOLDER',
    yesVotes: 4,
    noVotes: 1,
    quorum: 3,
    approvalBps: 5000,
    endRound: 6200000,
    executed: false,
    closed: false,
  },
  {
    id: 2,
    title: 'Workshop grants',
    description: 'Pay for a speaker honorarium and slide deck printing.',
    amount: 800000,
    recipient: 'RECIPIENT-ADDRESS-PLACEHOLDER',
    yesVotes: 6,
    noVotes: 0,
    quorum: 4,
    approvalBps: 5000,
    endRound: 6200100,
    executed: true,
    closed: true,
  },
];

export default function App() {
  const [wallet, setWallet] = useState<WalletName>('Disconnected');
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');
  const [proposals, setProposals] = useState(seedProposals);
  const [treasuryBalance] = useState(7_250_000);
  const [form, setForm] = useState({ title: '', description: '', amount: '', recipient: '', quorum: '3', approvalBps: '5000', duration: '5760' });

  const appAddress = useMemo(() => (APP_ID > 0 ? getAppAddress(APP_ID) : 'APP ID NOT CONFIGURED'), []);

  async function connectPera(): Promise<void> {
    try {
      const accounts = await connectWallet('Pera');
      setAddress(accounts[0] ?? '');
      setWallet(accounts.length > 0 ? 'Pera' : 'Disconnected');
      setError(accounts.length > 0 ? '' : 'No Pera accounts returned. Unlock wallet and try again.');
    } catch (connectError) {
      setError(connectError instanceof Error ? connectError.message : 'Failed to connect Pera Wallet.');
      setWallet('Disconnected');
    }
  }

  async function connectAlgoSigner(): Promise<void> {
    try {
      const accounts = await connectWallet('AlgoSigner');
      setAddress(accounts[0] ?? '');
      setWallet(accounts.length > 0 ? 'AlgoSigner' : 'Disconnected');
      setError(accounts.length > 0 ? '' : 'AlgoSigner was not found in this browser.');
    } catch (connectError) {
      setError(connectError instanceof Error ? connectError.message : 'Failed to connect AlgoSigner.');
      setWallet('Disconnected');
    }
  }

  async function submitProposal(): Promise<void> {
    const nextId = Math.max(...proposals.map((proposal) => proposal.id)) + 1;
    setProposals((current) => [
      {
        id: nextId,
        title: form.title,
        description: form.description,
        amount: Number(form.amount),
        recipient: form.recipient,
        yesVotes: 0,
        noVotes: 0,
        quorum: Number(form.quorum),
        approvalBps: Number(form.approvalBps),
        endRound: 6200000 + Number(form.duration),
        executed: false,
        closed: false,
      },
      ...current,
    ]);
    setForm({ title: '', description: '', amount: '', recipient: '', quorum: '3', approvalBps: '5000', duration: '5760' });
  }

  async function vote(proposalId: number, support: 0 | 1): Promise<void> {
    setProposals((current) => current.map((proposal) => {
      if (proposal.id !== proposalId || proposal.executed || proposal.closed) {
        return proposal;
      }
      return {
        ...proposal,
        yesVotes: proposal.yesVotes + (support === 1 ? 1 : 0),
        noVotes: proposal.noVotes + (support === 0 ? 1 : 0),
      };
    }));

    if (wallet !== 'Disconnected') {
      const params = await getSuggestedParams();
      void params;
    }
  }

  async function execute(proposalId: number): Promise<void> {
    setProposals((current) => current.map((proposal) => {
      if (proposal.id !== proposalId || proposal.executed) {
        return proposal;
      }
      const totalVotes = proposal.yesVotes + proposal.noVotes;
      const approved = totalVotes >= proposal.quorum && proposal.yesVotes * 10000 >= totalVotes * proposal.approvalBps;
      return approved ? { ...proposal, executed: true, closed: true } : proposal;
    }));
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Algorand DAO Treasury Voting Wallet</p>
          <h1>Transparent treasury spending for small communities.</h1>
          <p className="hero__copy">
            Proposal creation, one-vote-per-wallet voting, quorum checks, and treasury release all happen through the smart contract.
          </p>
        </div>
        <div className="hero__panel">
          <div>
            <span>Treasury balance</span>
            <strong>{formatAlgo(treasuryBalance)} ALGO</strong>
          </div>
          <div>
            <span>App address</span>
            <strong className="mono">{appAddress}</strong>
          </div>
          <div>
            <span>Wallet</span>
            <strong>{wallet}</strong>
          </div>
          <div>
            <span>Connected address</span>
            <strong className="mono">{address || 'Not connected'}</strong>
          </div>
        </div>
      </section>

      <section className="toolbar">
        <button onClick={connectPera}>Connect Pera Wallet</button>
        <button className="secondary" onClick={connectAlgoSigner}>Connect AlgoSigner</button>
      </section>

      {error ? <section className="panel">{error}</section> : null}

      <section className="grid">
        <div className="panel">
          <h2>Create Proposal</h2>
          <div className="form-grid">
            <input placeholder="Title" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
            <input placeholder="Recipient address" value={form.recipient} onChange={(event) => setForm({ ...form, recipient: event.target.value })} />
            <textarea placeholder="Description" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
            <input placeholder="Amount in microAlgos" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} />
            <input placeholder="Quorum" value={form.quorum} onChange={(event) => setForm({ ...form, quorum: event.target.value })} />
            <input placeholder="Approval BPS" value={form.approvalBps} onChange={(event) => setForm({ ...form, approvalBps: event.target.value })} />
            <input placeholder="Duration in rounds" value={form.duration} onChange={(event) => setForm({ ...form, duration: event.target.value })} />
          </div>
          <button onClick={submitProposal}>Submit proposal</button>
        </div>

        <div className="panel">
          <h2>Transaction Flow</h2>
          <ol className="flow-list">
            <li>Wallet connects and signs the app call locally.</li>
            <li>Contract stores immutable proposal metadata in boxes.</li>
            <li>Voters submit one vote per wallet per proposal.</li>
            <li>After deadline, anyone can execute if quorum and approval pass.</li>
          </ol>
          <div className="flow-note">
            Frontend signs with wallet, backend only reads chain state, and the contract releases treasury funds with an inner transaction.
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="section-head">
          <h2>Proposals</h2>
          <span>{proposals.length} total</span>
        </div>
        <div className="proposal-list">
          {proposals.map((proposal) => (
            <ProposalCard
              key={proposal.id}
              proposal={proposal}
              onVoteYes={(proposalId) => void vote(proposalId, 1)}
              onVoteNo={(proposalId) => void vote(proposalId, 0)}
              onExecute={(proposalId) => void execute(proposalId)}
            />
          ))}
        </div>
      </section>
    </main>
  );
}
