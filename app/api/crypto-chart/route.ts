import { NextRequest, NextResponse } from 'next/server';
import { COINGECKO_BASE } from '@/lib/crypto-api';

// Cache for 5 minutes (historical data doesn't change)
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000;

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const coinId = searchParams.get('id') || 'bitcoin';
  const days = searchParams.get('days') || '30';

  const cacheKey = `chart:${coinId}:${days}`;
  const cached = cache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return NextResponse.json(cached.data);
  }

  try {
    // Fetch historical price data
    const url = `${COINGECKO_BASE}/coins/${coinId}/ohlc?vs_currency=usd&days=${days}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      if (response.status === 429) {
        if (cached) {
          return NextResponse.json(cached.data);
        }
        return NextResponse.json({ error: 'Rate limit reached' }, { status: 429 });
      }
      throw new Error('Failed to fetch historical data');
    }

    const data = await response.json();
    
    // Convert OHLC data to chart-friendly format
    // CoinGecko returns: [timestamp, open, high, low, close]
    const chartData = data.map((item: number[]) => ({
      timestamp: item[0],
      date: new Date(item[0]).toISOString().split('T')[0],
      open: item[1],
      high: item[2],
      low: item[3],
      close: item[4]
    }));

    cache.set(cacheKey, { data: chartData, timestamp: Date.now() });
    console.log(`💾 Cached ${coinId} chart (${chartData.length} data points)`);

    return NextResponse.json(chartData);
  } catch (error) {
    console.error('Error fetching crypto chart data:', error);
    if (cached) {
      return NextResponse.json(cached.data);
    }
    return NextResponse.json(
      { error: 'Failed to fetch chart data' },
      { status: 500 }
    );
  }
}
