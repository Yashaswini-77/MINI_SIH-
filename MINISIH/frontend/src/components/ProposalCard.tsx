import { Proposal } from '../types';

export function ProposalCard({ proposal, onVoteYes, onVoteNo, onExecute }: {
  proposal: Proposal;
  onVoteYes: (id: number) => void;
  onVoteNo: (id: number) => void;
  onExecute: (id: number) => void;
}) {
  const totalVotes = proposal.yesVotes + proposal.noVotes;
  const yesRatio = totalVotes === 0 ? 0 : Math.round((proposal.yesVotes / totalVotes) * 100);
  const status = proposal.executed ? 'Executed' : proposal.closed ? 'Closed' : 'Active';

  return (
    <article className="proposal-card">
      <div className="proposal-card__header">
        <div>
          <p className="proposal-card__eyebrow">Proposal #{proposal.id}</p>
          <h3>{proposal.title}</h3>
        </div>
        <span className={`status status--${status.toLowerCase()}`}>{status}</span>
      </div>

      <p className="proposal-card__description">{proposal.description}</p>

      <dl className="proposal-card__grid">
        <div>
          <dt>Amount</dt>
          <dd>{proposal.amount.toLocaleString()} microAlgos</dd>
        </div>
        <div>
          <dt>Recipient</dt>
          <dd className="mono">{proposal.recipient}</dd>
        </div>
        <div>
          <dt>Votes</dt>
          <dd>{proposal.yesVotes} yes / {proposal.noVotes} no</dd>
        </div>
        <div>
          <dt>Approval</dt>
          <dd>{yesRatio}% yes</dd>
        </div>
      </dl>

      <div className="proposal-card__actions">
        <button onClick={() => onVoteYes(proposal.id)} disabled={proposal.executed || proposal.closed}>Vote Yes</button>
        <button className="secondary" onClick={() => onVoteNo(proposal.id)} disabled={proposal.executed || proposal.closed}>Vote No</button>
        <button className="ghost" onClick={() => onExecute(proposal.id)} disabled={proposal.executed}>Execute</button>
      </div>
    </article>
  );
}
