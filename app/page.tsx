'use client';

import { useEffect, useState } from 'react';
import { StockQuoteCard } from '@/components/stock-quote-card';
import { StockChart } from '@/components/stock-chart';
import { NewsFeed } from '@/components/news-feed';
import { ChatInterface } from '@/components/chat-interface';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, TrendingUp, BarChart3, Newspaper, MessageSquare, Activity } from 'lucide-react';
import Link from 'next/link';

// Sample watchlist stocks
const DEFAULT_WATCHLIST = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA'];

export default function Dashboard() {
  const [searchSymbol, setSearchSymbol] = useState('');
  const [watchlist, setWatchlist] = useState(DEFAULT_WATCHLIST);
  const [selectedStock, setSelectedStock] = useState('AAPL');
  const [stockDataMap, setStockDataMap] = useState<Record<string, any>>({});
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [newsData, setNewsData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [reportGenerated, setReportGenerated] = useState(false);

  // Fetch stock data when report is generated
  useEffect(() => {
    if (!reportGenerated) return;

    async function fetchStockData() {
      setLoading(true);
      try {
        // Fetch quotes for ALL watchlist stocks
        const fetchPromises = watchlist.map(async (symbol) => {
          const quoteRes = await fetch(`/api/stock?symbol=${symbol}`);
          const quoteData = await quoteRes.json();
          return { symbol, data: quoteData };
        });
        
        const results = await Promise.all(fetchPromises);
        const dataMap = Object.fromEntries(results.map(({ symbol, data }) => [symbol, data]));
        setStockDataMap(dataMap);

        // Fetch time series for selected stock
        const seriesRes = await fetch(`/api/stock-series?symbol=${selectedStock}`);
        const seriesData = await seriesRes.json();
        
        // Only update if we got valid array data
        if (Array.isArray(seriesData)) {
          setTimeSeriesData(seriesData);
        } else {
          console.warn('Time series returned non-array:', seriesData);
          setTimeSeriesData([]);
        }

        // Fetch news for selected stock
        const newsRes = await fetch(`/api/news?symbol=${selectedStock}`);
        const news = await newsRes.json();
        setNewsData(news);
      } catch (error) {
        console.error('Error fetching stock data:', error);
        setTimeSeriesData([]);
      } finally {
        setLoading(false);
      }
    }

    fetchStockData();
  }, [selectedStock, reportGenerated, watchlist]);

  const handleSearch = () => {
    if (searchSymbol.trim()) {
      const symbol = searchSymbol.toUpperCase().trim();
      if (!watchlist.includes(symbol)) {
        setWatchlist([...watchlist, symbol]);
      }
      setSelectedStock(symbol);
      // Auto-generate report when searching
      setReportGenerated(true);
      setSearchSymbol('');
    }
  };

  const handleGenerateReport = () => {
    setReportGenerated(true);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">Katsu Finance</h1>
                <p className="text-sm text-muted-foreground">Your AI-Powered Financial Dashboard</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link href="/economic-data">
                <Button variant="outline" size="sm" className="gap-2">
                  <Activity className="h-4 w-4" />
                  Economic Data
                </Button>
              </Link>
              <Link href="/treasury-yields">
                <Button variant="outline" size="sm" className="gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Yield Curve
                </Button>
              </Link>
              <Link href="/crypto">
                <Button variant="outline" size="sm" className="gap-2">
                  <Activity className="h-4 w-4" />
                  Crypto
                </Button>
              </Link>
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Search stock symbol..."
                  value={searchSymbol}
                  onChange={(e) => setSearchSymbol(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-64"
                />
                <Button
                  size="sm"
                  onClick={handleSearch}
                  className="absolute right-0 top-0 h-full px-3"
                >
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Generate Report Button */}
        {!reportGenerated ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">Ready to Analyze the Market?</h2>
              <p className="text-muted-foreground mb-6 max-w-md">
                Generate a comprehensive market report with real-time stock data, price charts, 
                and the latest financial news from multiple sources.
              </p>
            </div>
            <Button 
              onClick={handleGenerateReport} 
              size="lg"
              className="gap-2 text-lg px-8 py-6"
            >
              <BarChart3 className="h-6 w-6" />
              Generate Market Report
            </Button>
            <p className="text-xs text-muted-foreground mt-4">
              Data from Alpha Vantage • FRED • BEA • Yahoo Finance
            </p>
          </div>
        ) : (
          <>
            {/* Report Header with Refresh Button */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <BarChart3 className="h-6 w-6" />
                Market Report
              </h2>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setReportGenerated(false);
                    setStockDataMap({});
                    setTimeSeriesData([]);
                    setNewsData([]);
                  }}
                >
                  Close Report
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleGenerateReport}
                  disabled={loading}
                  className="gap-2"
                >
                  {loading ? 'Loading...' : 'Refresh Data'}
                  <BarChart3 className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Watchlist & Charts */}
              <div className="lg:col-span-2 space-y-6">
            {/* Stock Quote Cards */}
            <section>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Watchlist
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {watchlist.map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => setSelectedStock(symbol)}
                    className={`text-left transition-all ${
                      selectedStock === symbol
                        ? 'ring-2 ring-primary ring-offset-2 rounded-xl'
                        : ''
                    }`}
                  >
                    <StockQuoteCard symbol={symbol} data={stockDataMap[symbol]} />
                  </button>
                ))}
              </div>
            </section>

            {/* Price Chart */}
            <section>
              <StockChart
                data={timeSeriesData}
                symbol={selectedStock}
                title="30-Day Price History"
              />
            </section>

            {/* News Feed */}
            <section>
              <NewsFeed news={newsData} />
            </section>
          </div>

          {/* Right Column - Chat */}
          <div className="lg:col-span-1">
            <ChatInterface />
              </div>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p>Katsu Finance Dashboard • Powered by OpenClaw AI</p>
            <p className="mt-1">
              Data provided by Alpha Vantage • For educational purposes only
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
