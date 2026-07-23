import { market } from "./api";
import type { MarketIndex } from "./api";

let _cache: MarketIndex[] | null = null;

export async function getMarketIndices(): Promise<MarketIndex[]> {
  if (_cache) return _cache;
  const data = await market.getIndices();
  _cache = data.indices;
  return _cache;
}

export function clearMarketCache(): void {
  _cache = null;
}
