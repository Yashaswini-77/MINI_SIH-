import algosdk, { type SuggestedParams } from 'algosdk';

export const ALGOD_ADDRESS = import.meta.env.VITE_ALGOD_ADDRESS ?? 'https://testnet-api.algonode.cloud';
export const ALGOD_TOKEN = import.meta.env.VITE_ALGOD_TOKEN ?? '';
export const APP_ID = Number(import.meta.env.VITE_APP_ID ?? '0');

export function getSuggestedParams(): Promise<SuggestedParams> {
  const client = new algosdk.Algodv2(ALGOD_TOKEN, ALGOD_ADDRESS, '');
  return client.getTransactionParams().do();
}

export function getAppAddress(appId: number): string {
  return algosdk.getApplicationAddress(appId).toString();
}

export function formatAlgo(microalgos: number): string {
  return (microalgos / 1_000_000).toFixed(6);
}
