import { NextRequest, NextResponse } from 'next/server';

const FRED_API_KEY = process.env.FRED_KEY || '21d934bc76b6214fb384542693fe02bc';

// Treasury yield series IDs from FRED
const YIELD_SERIES: Record<string, string> = {
  '1MO': 'DGS1MO',
  '3MO': 'DGS3MO',
  '6MO': 'DGS6MO',
  '1Y': 'DGS1',
  '2Y': 'DGS2',
  '3Y': 'DGS3',
  '5Y': 'DGS5',
  '7Y': 'DGS7',
  '10Y': 'DGS10',
  '20Y': 'DGS20',
  '30Y': 'DGS30',
};

async function fetchYield(seriesId: string): Promise<{ value: number | null; date: string } | null> {
  try {
    // Fetch with descending order to get most recent first
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&file_type=json&api_key=${FRED_API_KEY}&limit=1&sort_order=desc`;
    const response = await fetch(url, { cache: 'no-store' });
    
    if (!response.ok) {
      console.error(`FRED API error for ${seriesId}:`, response.status);
      return null;
    }
    
    const data = await response.json();
    const observations = data.observations || [];
    
    // Get first observation with a value (most recent due to desc sort)
    const latest = observations.find((obs: any) => obs.value !== '.');
    if (latest) {
      return {
        value: parseFloat(latest.value),
        date: latest.date,
      };
    }
    return null;
  } catch (error) {
    console.error(`Error fetching ${seriesId}:`, error);
    return null;
  }
}

export async function GET(request: NextRequest) {
  try {
    // Fetch all yields in parallel
    const yieldPromises = Object.entries(YIELD_SERIES).map(
      async ([maturity, seriesId]) => {
        const result = await fetchYield(seriesId);
        return [maturity, result];
      }
    );
    
    const results = await Promise.all(yieldPromises);
    const yields: Record<string, { value: number | null; date: string }> = Object.fromEntries(results);

    // Calculate key spreads
    const spread10y2y = yields['10Y']?.value !== null && yields['2Y']?.value !== null
      ? yields['10Y'].value! - yields['2Y'].value!
      : null;

    const spread10y3mo = yields['10Y']?.value !== null && yields['3MO']?.value !== null
      ? yields['10Y'].value! - yields['3MO'].value!
      : null;

    const spread30y5y = yields['30Y']?.value !== null && yields['5Y']?.value !== null
      ? yields['30Y'].value! - yields['5Y'].value!
      : null;

    // Determine curve status
    const isInverted = spread10y2y !== null && spread10y2y < 0;
    const isFlattening = spread10y2y !== null && spread10y2y < 0.5 && spread10y2y > 0;
    const isNormal = spread10y2y !== null && spread10y2y >= 0.5;

    return NextResponse.json({
      yields,
      spreads: {
        '10Y-2Y': spread10y2y,
        '10Y-3MO': spread10y3mo,
        '30Y-5Y': spread30y5y,
      },
      curveStatus: {
        status: isInverted ? 'inverted' : isFlattening ? 'flattening' : isNormal ? 'normal' : 'unknown',
        isInverted,
        isFlattening,
        isNormal,
      },
      lastUpdated: yields['10Y']?.date || null,
    });

  } catch (error) {
    console.error('Error fetching treasury yields:', error);
    return NextResponse.json(
      { error: 'Failed to fetch treasury yields' },
      { status: 500 }
    );
  }
}
