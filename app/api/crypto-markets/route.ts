import { NextRequest, NextResponse } from 'next/server';
import { COINGECKO_BASE } from '@/lib/crypto-api';

// Cache for 2 minutes
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 2 * 60 * 1000;

export async function GET(request: NextRequest) {
  const cacheKey = 'market';
  const cached = cache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return NextResponse.json(cached.data);
  }

  try {
    // Fetch top 50 coins by market cap
    const url = `${COINGECKO_BASE}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false`;
    const response = await fetch(url);
    
    if (!response.ok) {
      if (response.status === 429) {
        if (cached) {
          return NextResponse.json(cached.data);
        }
        return NextResponse.json({ error: 'Rate limit reached' }, { status: 429 });
      }
      throw new Error('Failed to fetch market data');
    }

    const data = await response.json();
    
    // Simplify the data
    const markets = data.map((coin: any) => ({
      id: coin.id,
      symbol: coin.symbol.toUpperCase(),
      name: coin.name,
      price: coin.current_price,
      marketCap: coin.market_cap,
      rank: coin.market_cap_rank,
      volume24h: coin.total_volume,
      change24h: coin.price_change_percentage_24h,
      change7d: coin.price_change_percentage_7d,
      circulatingSupply: coin.circulating_supply,
      high24h: coin.high_24h,
      low24h: coin.low_24h,
      image: coin.image
    }));

    cache.set(cacheKey, { data: markets, timestamp: Date.now() });
    console.log(`💾 Cached market data (${markets.length} coins)`);

    return NextResponse.json(markets);
  } catch (error) {
    console.error('Error fetching market data:', error);
    if (cached) {
      return NextResponse.json(cached.data);
    }
    return NextResponse.json(
      { error: 'Failed to fetch market data' },
      { status: 500 }
    );
  }
}
