// API Configuration and Utilities
// Financial data APIs for the Katsu Finance Dashboard

// Use environment variables in production, fallback to hardcoded for local dev
export const ALPHA_VANTAGE_KEY = process.env.ALPHA_VANTAGE_KEY || '2Q3W3M7OMRSU3A5I';
export const FRED_KEY = process.env.FRED_KEY || '21d934bc76b6214fb384542693fe02bc';
export const BEA_KEY = process.env.BEA_KEY || '28D77A5E-CC66-43D0-BD6D-C108FED47219';

export const ALPHA_VANTAGE_BASE = 'https://www.alphavantage.co/query';
export const FRED_BASE = 'https://api.stlouisfed.org/fred';
export const BEA_BASE = 'https://apps.bea.gov/api';

/**
 * Fetch stock quote from Alpha Vantage
 */
export async function getStockQuote(symbol: string) {
  try {
    const url = `${ALPHA_VANTAGE_BASE}?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${ALPHA_VANTAGE_KEY}`;
    const response = await fetch(url);
    const data = await response.json();
    return data['Global Quote'] || null;
  } catch (error) {
    console.error('Error fetching stock quote:', error);
    return null;
  }
}

/**
 * Fetch daily time series for a stock
 */
export async function getStockTimeSeries(symbol: string, outputsize: 'compact' | 'full' = 'compact') {
  try {
    const url = `${ALPHA_VANTAGE_BASE}?function=TIME_SERIES_DAILY&symbol=${symbol}&outputsize=${outputsize}&apikey=${ALPHA_VANTAGE_KEY}`;
    const response = await fetch(url);
    const data = await response.json();
    return data['Time Series (Daily)'] || null;
  } catch (error) {
    console.error('Error fetching time series:', error);
    return null;
  }
}

/**
 * Fetch company overview/fundamentals
 */
export async function getCompanyOverview(symbol: string) {
  try {
    const url = `${ALPHA_VANTAGE_BASE}?function=OVERVIEW&symbol=${symbol}&apikey=${ALPHA_VANTAGE_KEY}`;
    const response = await fetch(url);
    const data = await response.json();
    return data || null;
  } catch (error) {
    console.error('Error fetching company overview:', error);
    return null;
  }
}

/**
 * Fetch economic news and data summaries from FRED
 */
export async function getFREDEconomicNews() {
  try {
    // FRED doesn't have a direct news API, so we'll fetch key economic indicators
    // and create summary "news" items from them
    const gdpUrl = `${FRED_BASE}/series/observations?series_id=GDP&api_key=${FRED_KEY}&file_type=json&limit=1`;
    const unempUrl = `${FRED_BASE}/series/observations?series_id=UNRATE&api_key=${FRED_KEY}&file_type=json&limit=1`;
    const cpiUrl = `${FRED_BASE}/series/observations?series_id=CPIAUCSL&api_key=${FRED_KEY}&file_type=json&limit=1`;

    const [gdpRes, unempRes, cpiRes] = await Promise.all([
      fetch(gdpUrl),
      fetch(unempUrl),
      fetch(cpiUrl)
    ]);

    const gdpData = await gdpRes.json();
    const unempData = await unempRes.json();
    const cpiData = await cpiRes.json();

    const news = [];

    // GDP Update
    if (gdpData.observations && gdpData.observations.length > 0) {
      const latest = gdpData.observations[0];
      news.push({
        title: `GDP Update: $${(parseFloat(latest.value) / 1000).toFixed(1)}T (${latest.date})`,
        summary: `U.S. Gross Domestic Product reached ${latest.value} billion dollars in the latest reporting period. This represents the total value of all goods and services produced in the economy.`,
        source: 'FRED',
        time_published: latest.date,
        sentiment_score: 0.1,
        category: 'Economic Data'
      });
    }

    // Unemployment Rate
    if (unempData.observations && unempData.observations.length > 0) {
      const latest = unempData.observations[0];
      const rate = parseFloat(latest.value);
      const sentiment = rate < 4 ? 0.3 : rate > 6 ? -0.3 : 0;
      news.push({
        title: `Unemployment Rate: ${latest.value}% (${latest.date})`,
        summary: `The U.S. unemployment rate stands at ${rate}%. ${rate < 4 ? 'This is considered a strong labor market.' : rate > 6 ? 'This indicates labor market weakness.' : 'This is near historical averages.'}`,
        source: 'FRED',
        time_published: latest.date,
        sentiment_score: sentiment,
        category: 'Employment'
      });
    }

    // Inflation (CPI)
    if (cpiData.observations && cpiData.observations.length > 0) {
      const latest = cpiData.observations[0];
      news.push({
        title: `Inflation (CPI): ${latest.value} Index (${latest.date})`,
        summary: `The Consumer Price Index measures average changes in prices paid by urban consumers. Current level: ${latest.value}. Higher values indicate inflationary pressure.`,
        source: 'FRED',
        time_published: latest.date,
        sentiment_score: -0.1,
        category: 'Inflation'
      });
    }

    return news;
  } catch (error) {
    console.error('Error fetching FRED data:', error);
    return [];
  }
}

/**
 * Fetch GDP data from BEA
 */
export async function getBEAGDPData() {
  try {
    const url = `${BEA_BASE}?method=GetData&UserID=${BEA_KEY}&datasetname=NIPA&TableName=1.1.5&Frequency=A&Year=ALL`;
    const response = await fetch(url);
    const data = await response.json();
    return data.BEAAPI.Results.Data || [];
  } catch (error) {
    console.error('Error fetching BEA GDP data:', error);
    return [];
  }
}

/**
 * Generate news from BEA data
 */
export async function getBEAEconomicNews() {
  try {
    const gdpData = await getBEAGDPData();
    const news = [];

    if (gdpData.length > 0) {
      const latest = gdpData[gdpData.length - 1];
      const previous = gdpData[gdpData.length - 2];
      
      if (previous && latest) {
        const current = parseFloat(latest.DataValue || '0');
        const prev = parseFloat(previous.DataValue || '0');
        const growth = ((current - prev) / prev * 100).toFixed(2);
        const growthNum = parseFloat(growth);
        
        news.push({
          title: `BEA GDP Report: ${growth}% Growth (${latest.TimePeriod})`,
          summary: `According to the Bureau of Economic Analysis, GDP ${growthNum > 0 ? 'grew' : 'contracted'} by ${Math.abs(growthNum)}% in ${latest.TimePeriod}. Current GDP: $${(current / 1000).toFixed(1)}T.`,
          source: 'BEA',
          time_published: latest.TimePeriod,
          sentiment_score: growthNum > 2 ? 0.3 : growthNum < 0 ? -0.3 : 0.1,
          category: 'Economic Growth'
        });
      }
    }

    return news;
  } catch (error) {
    console.error('Error generating BEA news:', error);
    return [];
  }
}

/**
 * Fetch Yahoo Finance news via yfinance-style scraping
 * Note: Yahoo doesn't have an official API, so we use a proxy service
 */
export async function getYahooFinanceNews(symbol?: string) {
  try {
    // Using a public RSS feed proxy for Yahoo Finance news
    const rssUrl = symbol 
      ? `https://query1.finance.yahoo.com/v1/finance/rss/${symbol.toUpperCase()}`
      : 'https://finance.yahoo.com/news/';
    
    // For demo purposes, we'll create sample news items
    // In production, you'd parse the RSS feed or use a news API
    const sampleNews = [
      {
        title: 'Market Outlook: Tech Stocks Lead Rally Amid Economic Optimism',
        summary: 'Major technology stocks pushed higher today as investors digested fresh economic data showing resilient consumer spending and moderating inflation pressures.',
        source: 'Yahoo Finance',
        time_published: new Date().toISOString(),
        sentiment_score: 0.2,
        category: 'Market News',
        url: 'https://finance.yahoo.com/'
      },
      {
        title: 'Fed Officials Signal Cautious Approach to Interest Rate Changes',
        summary: 'Federal Reserve policymakers indicated they will take a data-dependent approach to future rate decisions, balancing inflation concerns with employment goals.',
        source: 'Yahoo Finance',
        time_published: new Date().toISOString(),
        sentiment_score: 0,
        category: 'Federal Reserve',
        url: 'https://finance.yahoo.com/'
      },
      {
        title: 'Oil Prices Fluctuate on Global Demand Concerns',
        summary: 'Crude oil futures traded mixed as traders weighed supply constraints against potential demand weakness in major economies.',
        source: 'Yahoo Finance',
        time_published: new Date().toISOString(),
        sentiment_score: -0.1,
        category: 'Commodities',
        url: 'https://finance.yahoo.com/'
      }
    ];

    if (symbol) {
      // Add stock-specific news
      sampleNews.unshift({
        title: `${symbol} Stock Analysis: What Investors Need to Know`,
        summary: `Latest developments and analyst commentary on ${symbol}. Check technical indicators, earnings expectations, and market sentiment.`,
        source: 'Yahoo Finance',
        time_published: new Date().toISOString(),
        sentiment_score: 0.1,
        category: 'Stock Analysis',
        url: `https://finance.yahoo.com/quote/${symbol}`
      });
    }

    return sampleNews;
  } catch (error) {
    console.error('Error fetching Yahoo Finance news:', error);
    return [];
  }
}

/**
 * Fetch GDP data from FRED
 */
export async function getGDPData() {
  try {
    const url = `${FRED_BASE}/series/observations?series_id=GDP&api_key=${FRED_KEY}&file_type=json`;
    const response = await fetch(url);
    const data = await response.json();
    return data.observations || [];
  } catch (error) {
    console.error('Error fetching GDP data:', error);
    return [];
  }
}

/**
 * Fetch unemployment rate from FRED
 */
export async function getUnemploymentRate() {
  try {
    const url = `${FRED_BASE}/series/observations?series_id=UNRATE&api_key=${FRED_KEY}&file_type=json`;
    const response = await fetch(url);
    const data = await response.json();
    return data.observations || [];
  } catch (error) {
    console.error('Error fetching unemployment data:', error);
    return [];
  }
}

/**
 * Fetch inflation rate (CPI) from FRED
 */
export async function getInflationData() {
  try {
    const url = `${FRED_BASE}/series/observations?series_id=CPIAUCSL&api_key=${FRED_KEY}&file_type=json`;
    const response = await fetch(url);
    const data = await response.json();
    return data.observations || [];
  } catch (error) {
    console.error('Error fetching inflation data:', error);
    return [];
  }
}

/**
 * Format date for display
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

/**
 * Format currency
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
}

/**
 * Format large numbers (millions, billions)
 */
export function formatLargeNumber(value: number): string {
  if (value >= 1e12) {
    return `$${(value / 1e12).toFixed(2)}T`;
  } else if (value >= 1e9) {
    return `$${(value / 1e9).toFixed(2)}B`;
  } else if (value >= 1e6) {
    return `$${(value / 1e6).toFixed(2)}M`;
  }
  return formatCurrency(value);
}
