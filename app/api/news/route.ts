import { NextRequest, NextResponse } from 'next/server';
import { getFREDEconomicNews, getBEAEconomicNews, getYahooFinanceNews, ALPHA_VANTAGE_KEY, ALPHA_VANTAGE_BASE } from '@/lib/api';
import { XMLParser } from 'fast-xml-parser';

// RSS Feed URLs
const RSS_FEEDS = {
  cnbc: {
    top: 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000115',
    markets: 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147',
    tech: 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910'
  },
  bloomberg: {
    markets: 'https://www.bloomberg.com/feed/podcast/markets.xml',
    technology: 'https://www.bloomberg.com/feed/podcast/technology.xml'
  },
  wsj: {
    markets: 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
    business: 'https://feeds.a.dj.com/rss/RSSOpinion.xml'
  }
};

interface NewsItem {
  title: string;
  summary: string;
  url: string;
  time_published: string;
  source: string;
  sourceColor: string;
  sentiment_score?: number;
  image?: string;
  category?: string;
}

// Parse RSS feed XML using fast-xml-parser
function parseRSSFeed(xml: string, sourceName: string, sourceColor: string): NewsItem[] {
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: '@_'
  });

  const result = parser.parse(xml);
  const items: NewsItem[] = [];

  const channel = result?.rss?.channel || result?.feed;
  const entries = channel?.item || [];
  const entryArray = Array.isArray(entries) ? entries : [entries];

  for (let i = 0; i < Math.min(entryArray.length, 10); i++) {
    const item = entryArray[i];
    const title = item?.title || '';
    const description = item?.description || item?.['content:encoded'] || '';
    const link = item?.link || '';
    const pubDate = item?.pubDate || '';
    const enclosure = item?.['@_url'] || item?.enclosure?.['@_url'] || item?.['media:content']?.['@_url'] || '';

    // Strip HTML tags from description
    const cleanSummary = description.replace(/<[^>]*>/g, '').substring(0, 200) + '...';

    items.push({
      title,
      summary: cleanSummary,
      url: link,
      time_published: pubDate,
      source: sourceName,
      sourceColor,
      image: enclosure || undefined
    });
  }

  return items;
}

// Fetch RSS feed with proper headers
async function fetchRSSFeed(url: string): Promise<string> {
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'application/rss+xml, application/xml, text/xml',
      'Accept-Language': 'en-US,en;q=0.9'
    },
    cache: 'no-store'
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch RSS: ${response.status}`);
  }

  return await response.text();
}

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
      sourceColor: 'bg-gray-600',
      sentiment_score: item.overall_sentiment_score,
      topics: item.topics
    })) as NewsItem[];
  } catch (error) {
    console.error('Error fetching Alpha Vantage news:', error);
    return [];
  }
}

async function getCNBCNews(): Promise<NewsItem[]> {
  try {
    const [topNews, marketsNews] = await Promise.all([
      fetchRSSFeed(RSS_FEEDS.cnbc.top),
      fetchRSSFeed(RSS_FEEDS.cnbc.markets)
    ]);

    const topItems = parseRSSFeed(topNews, 'CNBC', 'bg-red-600');
    const marketItems = parseRSSFeed(marketsNews, 'CNBC', 'bg-red-600');

    return [...topItems, ...marketItems].slice(0, 15);
  } catch (error) {
    console.error('Error fetching CNBC news:', error);
    return [];
  }
}

async function getBloombergNews(): Promise<NewsItem[]> {
  try {
    const marketsXml = await fetchRSSFeed(RSS_FEEDS.bloomberg.markets);
    const items = parseRSSFeed(marketsXml, 'Bloomberg', 'bg-blue-600');
    return items.slice(0, 10);
  } catch (error) {
    console.error('Error fetching Bloomberg news:', error);
    return [];
  }
}

async function getWSJNews(): Promise<NewsItem[]> {
  try {
    const [marketsXml, businessXml] = await Promise.all([
      fetchRSSFeed(RSS_FEEDS.wsj.markets),
      fetchRSSFeed(RSS_FEEDS.wsj.business)
    ]);

    const marketItems = parseRSSFeed(marketsXml, 'WSJ', 'bg-gray-900');
    const businessItems = parseRSSFeed(businessXml, 'WSJ', 'bg-gray-900');

    return [...marketItems, ...businessItems].slice(0, 15);
  } catch (error) {
    console.error('Error fetching WSJ news:', error);
    return [];
  }
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const symbol = searchParams.get('symbol');
  const includeEconomic = searchParams.get('economic') === 'true';

  try {
    let news: NewsItem[] = [];

    if (includeEconomic) {
      // Combine all sources
      const [
        stockNews,
        cnbcNews,
        bloombergNews,
        wsjNews,
        fredNews,
        beaNews
      ] = await Promise.all([
        symbol ? getAlphaVantageNews(symbol) : Promise.resolve([]),
        getCNBCNews(),
        getBloombergNews(),
        getWSJNews(),
        getFREDEconomicNews(),
        getBEAEconomicNews()
      ]);

      // Ensure all news items have required fields
      const normalizeNews = (item: any): NewsItem => ({
        title: item.title || 'No Title',
        summary: item.summary || '',
        url: item.url || '#',
        time_published: item.time_published || new Date().toISOString(),
        source: item.source || 'Unknown',
        sourceColor: item.sourceColor || 'bg-gray-600',
        category: item.category || 'General',
        sentiment_score: item.sentiment_score
      });

      const allNews = [...cnbcNews, ...bloombergNews, ...wsjNews, ...stockNews, ...fredNews, ...beaNews];
      news = allNews.map(normalizeNews);
      
      // Sort by time (newest first)
      news.sort((a, b) => {
        const dateA = new Date(a.time_published || 0).getTime();
        const dateB = new Date(b.time_published || 0).getTime();
        return dateB - dateA;
      });

      // Return top 30
      return NextResponse.json(news.slice(0, 30));
    } else if (symbol) {
      // Stock-specific: Alpha Vantage + major sources
      const [stockNews, cnbcNews, bloombergNews, wsjNews] = await Promise.all([
        getAlphaVantageNews(symbol),
        getCNBCNews(),
        getBloombergNews(),
        getWSJNews()
      ]);

      // Filter for symbol mentions in title
      const symbolUpper = symbol.toUpperCase();
      const filteredNews = [
        ...stockNews,
        ...cnbcNews.filter(n => n.title.toUpperCase().includes(symbolUpper)),
        ...bloombergNews.filter(n => n.title.toUpperCase().includes(symbolUpper)),
        ...wsjNews.filter(n => n.title.toUpperCase().includes(symbolUpper))
      ];

      filteredNews.sort((a, b) => {
        const dateA = new Date(a.time_published || 0).getTime();
        const dateB = new Date(b.time_published || 0).getTime();
        return dateB - dateA;
      });

      return NextResponse.json(filteredNews.slice(0, 20));
    } else {
      // General financial news from all premium sources
      const [cnbcNews, bloombergNews, wsjNews] = await Promise.all([
        getCNBCNews(),
        getBloombergNews(),
        getWSJNews()
      ]);

      news = [...cnbcNews, ...bloombergNews, ...wsjNews];
      
      // Sort by time
      news.sort((a, b) => {
        const dateA = new Date(a.time_published || 0).getTime();
        const dateB = new Date(b.time_published || 0).getTime();
        return dateB - dateA;
      });

      return NextResponse.json(news.slice(0, 30));
    }
  } catch (error) {
    console.error('Error fetching news:', error);
    // Fallback to Yahoo Finance if everything else fails
    const fallbackNews = await getYahooFinanceNews(symbol || undefined);
    return NextResponse.json(fallbackNews);
  }
}
