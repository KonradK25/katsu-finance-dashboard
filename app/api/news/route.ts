import { NextRequest, NextResponse } from 'next/server';
import { getFREDEconomicNews, getBEAEconomicNews, getYahooFinanceNews, ALPHA_VANTAGE_KEY, ALPHA_VANTAGE_BASE } from '@/lib/api';

async function getAlphaVantageNews(symbol: string) {
  try {
    let url = `${ALPHA_VANTAGE_BASE}?function=NEWS_SENTIMENT&apikey=${ALPHA_VANTAGE_KEY}&tickers=${symbol.toUpperCase()}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch news');
    }

    const data = await response.json();
    const feed = data.feed || [];

    return feed.map((item: any) => ({
      title: item.title,
      summary: item.summary,
      url: item.url,
      time_published: item.time_published,
      source: item.source,
      sentiment_score: item.overall_sentiment_score,
      topics: item.topics
    }));
  } catch (error) {
    console.error('Error fetching Alpha Vantage news:', error);
    return [];
  }
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const symbol = searchParams.get('symbol');
  const includeEconomic = searchParams.get('economic') === 'true';

  try {
    let news = [];

    if (includeEconomic) {
      // Combine Alpha Vantage stock news with economic data
      const [stockNews, fredNews, beaNews] = await Promise.all([
        symbol ? getAlphaVantageNews(symbol) : Promise.resolve([]),
        getFREDEconomicNews(),
        getBEAEconomicNews()
      ]);

      news = [...stockNews, ...fredNews, ...beaNews];
      
      // Sort by time (newest first)
      news.sort((a, b) => {
        const dateA = new Date(a.time_published || 0).getTime();
        const dateB = new Date(b.time_published || 0).getTime();
        return dateB - dateA;
      });
    } else if (symbol) {
      // Use Alpha Vantage for stock-specific news
      news = await getAlphaVantageNews(symbol);
    } else {
      // Default: Yahoo Finance general news
      news = await getYahooFinanceNews();
    }

    return NextResponse.json(news);
  } catch (error) {
    console.error('Error fetching news:', error);
    // Fallback to Yahoo Finance if everything else fails
    const fallbackNews = await getYahooFinanceNews(symbol || undefined);
    return NextResponse.json(fallbackNews);
  }
}
