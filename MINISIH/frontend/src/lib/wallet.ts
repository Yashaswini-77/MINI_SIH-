import algosdk, { type SuggestedParams, type Transaction } from 'algosdk';

declare global {
  interface Window {
    AlgoSigner?: {
      connect: () => Promise<void>;
      accounts: (args: { ledger: string }) => Promise<Array<{ address: string }>>;
    };
  }
}

export type WalletProvider = 'Pera' | 'AlgoSigner';

export async function connectWallet(provider: WalletProvider): Promise<string[]> {
  if (provider === 'Pera') {
    const module = await import('@perawallet/connect');
    const typedModule = module as unknown as {
      PeraWalletConnect?: new () => { connect: () => Promise<string[]> };
      default?: new () => { connect: () => Promise<string[]> };
    };
    const PeraConnector = typedModule.PeraWalletConnect ?? typedModule.default;
    if (!PeraConnector) {
      return [];
    }
    const peraWallet = new PeraConnector();
    return peraWallet.connect();
  }

  if (!window.AlgoSigner) {
    return [];
  }

  await window.AlgoSigner.connect();
  const accounts = await window.AlgoSigner.accounts({ ledger: 'TestNet' });
  return accounts.map((account) => account.address);
}

export function buildCreateProposalTxn(args: {
  sender: string;
  appId: number;
  params: SuggestedParams;
  title: string;
  description: string;
  amount: number;
  recipient: string;
  quorum: number;
  approvalBps: number;
  duration: number;
}): Transaction {
  return algosdk.makeApplicationNoOpTxnFromObject({
    sender: args.sender,
    appIndex: args.appId,
    suggestedParams: args.params,
    appArgs: [
      new Uint8Array(new TextEncoder().encode('create_proposal')),
      new Uint8Array(new TextEncoder().encode(args.title)),
      new Uint8Array(new TextEncoder().encode(args.description)),
      algosdk.encodeUint64(args.amount),
      algosdk.decodeAddress(args.recipient).publicKey,
      algosdk.encodeUint64(args.quorum),
      algosdk.encodeUint64(args.approvalBps),
      algosdk.encodeUint64(args.duration),
    ],
  });
}

export function buildVoteTxn(args: {
  sender: string;
  appId: number;
  params: SuggestedParams;
  proposalId: number;
  support: 0 | 1;
}): Transaction {
  return algosdk.makeApplicationNoOpTxnFromObject({
    sender: args.sender,
    appIndex: args.appId,
    suggestedParams: args.params,
    appArgs: [
      new Uint8Array(new TextEncoder().encode('vote')),
      algosdk.encodeUint64(args.proposalId),
      algosdk.encodeUint64(args.support),
    ],
  });
}

export function buildExecuteTxn(args: {
  sender: string;
  appId: number;
  params: SuggestedParams;
  proposalId: number;
}): Transaction {
  return algosdk.makeApplicationNoOpTxnFromObject({
    sender: args.sender,
    appIndex: args.appId,
    suggestedParams: args.params,
    appArgs: [new Uint8Array(new TextEncoder().encode('execute')), algosdk.encodeUint64(args.proposalId)],
  });
}
