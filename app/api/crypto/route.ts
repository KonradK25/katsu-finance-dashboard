import { NextRequest, NextResponse } from 'next/server';
import { COINGECKO_BASE } from '@/lib/crypto-api';

// Simple in-memory cache (2 minutes for crypto - prices change fast)
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 2 * 60 * 1000; // 2 minutes

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const coinId = searchParams.get('id') || 'bitcoin';

  const cacheKey = `coin:${coinId}`;
  const cached = cache.get(cacheKey);
  
  // Return cached data if still valid
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return NextResponse.json(cached.data);
  }

  try {
    const url = `${COINGECKO_BASE}/coins/${coinId}`;
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 429) {
        // Rate limited - return cached data if available
        if (cached) {
          console.log('📦 Returning stale crypto cache due to rate limit');
          return NextResponse.json(cached.data);
        }
        return NextResponse.json({ error: 'CoinGecko rate limit reached' }, { status: 429 });
      }
      throw new Error(`CoinGecko API error: ${response.status}`);
    }

    const data = await response.json();
    
    // Extract key data
    const quote = {
      id: data.id,
      symbol: data.symbol?.toUpperCase(),
      name: data.name,
      price: data.market_data?.current_price?.usd || 0,
      marketCap: data.market_data?.market_cap?.usd || 0,
      volume24h: data.market_data?.total_volume?.usd || 0,
      change24h: data.market_data?.price_change_percentage_24h || 0,
      change7d: data.market_data?.price_change_percentage_7d_in_currency?.usd || 0,
      circulatingSupply: data.market_data?.circulating_supply || 0,
      totalSupply: data.market_data?.total_supply || 0,
      high24h: data.market_data?.high_24h?.usd || 0,
      low24h: data.market_data?.low_24h?.usd || 0,
      lastUpdated: data.last_updated
    };

    // Cache the result
    cache.set(cacheKey, { data: quote, timestamp: Date.now() });
    console.log(`💾 Cached ${coinId} at $${quote.price.toLocaleString()}`);

    return NextResponse.json(quote);
  } catch (error) {
    console.error('Error fetching crypto data:', error);
    // Return cached data on error if available
    if (cached) {
      console.log(`📦 Returning stale cache for ${coinId}`);
      return NextResponse.json(cached.data);
    }
    return NextResponse.json(
      { error: 'Failed to fetch crypto data', details: String(error) },
      { status: 500 }
    );
  }
}
