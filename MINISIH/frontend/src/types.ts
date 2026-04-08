export type Proposal = {
  id: number;
  title: string;
  description: string;
  amount: number;
  recipient: string;
  yesVotes: number;
  noVotes: number;
  quorum: number;
  approvalBps: number;
  endRound: number;
  executed: boolean;
  closed: boolean;
};

export type WalletName = 'Pera' | 'AlgoSigner' | 'Disconnected';
