import { NextRequest, NextResponse } from 'next/server';
import { getFREDEconomicNews, getBEAEconomicNews, getYahooFinanceNews } from '@/lib/api';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const symbol = searchParams.get('symbol');
  const source = searchParams.get('source'); // 'all', 'fred', 'bea', 'yahoo'

  try {
    let news = [];

    if (source === 'fred') {
      // Only FRED economic data
      news = await getFREDEconomicNews();
    } else if (source === 'bea') {
      // Only BEA economic data
      news = await getBEAEconomicNews();
    } else if (source === 'yahoo') {
      // Only Yahoo Finance news
      news = await getYahooFinanceNews(symbol || undefined);
    } else {
      // Combine all sources (default)
      const [fredNews, beaNews, yahooNews] = await Promise.all([
        getFREDEconomicNews(),
        getBEAEconomicNews(),
        getYahooFinanceNews(symbol || undefined)
      ]);

      news = [...fredNews, ...beaNews, ...yahooNews];
      
      // Sort by time (newest first)
      news.sort((a, b) => {
        const dateA = new Date(a.time_published || 0).getTime();
        const dateB = new Date(b.time_published || 0).getTime();
        return dateB - dateA;
      });
    }

    return NextResponse.json(news);
  } catch (error) {
    console.error('Error fetching combined news:', error);
    return NextResponse.json(
      { error: 'Failed to fetch news from multiple sources' },
      { status: 500 }
    );
  }
}
