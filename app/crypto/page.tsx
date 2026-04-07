'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, TrendingUp, TrendingDown, DollarSign, Activity, BarChart3, Lightbulb } from 'lucide-react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import Link from 'next/link';

interface CryptoData {
  id: string;
  symbol: string;
  name: string;
  price: number;
  marketCap: number;
  rank: number;
  volume24h: number;
  change24h: number;
  change7d: number;
  circulatingSupply: number;
  high24h: number;
  low24h: number;
  image?: string;
}

interface ChartDataPoint {
  date: string;
  price: number;
}

export default function CryptoDashboard() {
  const [cryptos, setCryptos] = useState<CryptoData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCrypto, setSelectedCrypto] = useState<string>('bitcoin');
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [chartLoading, setChartLoading] = useState(false);

  // Fetch market data
  useEffect(() => {
    async function fetchMarketData() {
      try {
        const res = await fetch('/api/crypto-markets');
        const data = await res.json();
        setCryptos(data);
      } catch (error) {
        console.error('Error fetching crypto data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchMarketData();
  }, []);

  // Fetch chart data when selected crypto changes
  useEffect(() => {
    async function fetchChartData() {
      setChartLoading(true);
      try {
        const res = await fetch(`/api/crypto-chart?id=${selectedCrypto}&days=30`);
        const data = await res.json();
        const formatted = data.map((item: any) => ({
          date: new Date(item.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          price: item.close
        }));
        setChartData(formatted);
      } catch (error) {
        console.error('Error fetching chart data:', error);
      } finally {
        setChartLoading(false);
      }
    }
    fetchChartData();
  }, [selectedCrypto]);

  const topGainer = cryptos.reduce((prev, current) => 
    (prev.change24h > current.change24h) ? prev : current
  , cryptos[0] || { change24h: 0 });

  const topLoser = cryptos.reduce((prev, current) => 
    (prev.change24h < current.change24h) ? prev : current
  , cryptos[0] || { change24h: 0 });

  const totalMarketCap = cryptos.reduce((sum, c) => sum + c.marketCap, 0);
  const totalVolume = cryptos.reduce((sum, c) => sum + c.volume24h, 0);

  const selectedData = cryptos.find(c => c.id === selectedCrypto);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="outline" size="sm" className="gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Dashboard
                </Button>
              </Link>
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30">
                  <Activity className="h-8 w-8 text-blue-400" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                    Crypto Dashboard
                  </h1>
                  <p className="text-sm text-muted-foreground">Real-time cryptocurrency prices & analytics</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-6">
        {/* Market Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Market Cap</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${(totalMarketCap / 1e12).toFixed(2)}T</div>
              <p className="text-xs text-muted-foreground mt-1">Top 50 cryptos</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">24h Volume</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${(totalVolume / 1e9).toFixed(2)}B</div>
              <p className="text-xs text-muted-foreground mt-1">Trading volume</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Top Gainer</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">{topGainer?.symbol || 'N/A'}</div>
              <p className="text-xs text-green-500 mt-1">+{topGainer?.change24h?.toFixed(2)}%</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Top Loser</CardTitle>
              <TrendingDown className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">{topLoser?.symbol || 'N/A'}</div>
              <p className="text-xs text-red-500 mt-1">{topLoser?.change24h?.toFixed(2)}%</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Crypto List */}
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Top 50 Cryptocurrencies
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {loading ? (
                    <p className="text-muted-foreground text-center py-8">Loading...</p>
                  ) : (
                    cryptos.map((crypto) => (
                      <button
                        key={crypto.id}
                        onClick={() => setSelectedCrypto(crypto.id)}
                        className={`w-full p-3 rounded-lg transition-all text-left ${
                          selectedCrypto === crypto.id
                            ? 'bg-primary/10 border border-primary/30'
                            : 'hover:bg-muted/50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <span className="text-xs font-medium text-muted-foreground w-6">#{crypto.rank}</span>
                            <div>
                              <p className="font-semibold">{crypto.symbol}</p>
                              <p className="text-xs text-muted-foreground">{crypto.name}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">${crypto.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}</p>
                            <p className={`text-xs ${crypto.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {crypto.change24h >= 0 ? '+' : ''}{crypto.change24h?.toFixed(2)}%
                            </p>
                          </div>
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right: Chart & Details */}
          <div className="lg:col-span-2 space-y-4">
            {/* Price Chart */}
            <Card>
              <CardHeader>
                <CardTitle>{selectedData?.name || 'Select a cryptocurrency'} - 30 Day Price Chart</CardTitle>
              </CardHeader>
              <CardContent>
                {chartLoading ? (
                  <div className="h-[300px] flex items-center justify-center">
                    <p className="text-muted-foreground">Loading chart...</p>
                  </div>
                ) : chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                      <XAxis dataKey="date" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v.toLocaleString()}`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: 'hsl(var(--background))', border: '1px solid hsl(var(--border))', borderRadius: 'var(--radius)' }}
                        formatter={(v: any) => [`$${Number(v).toLocaleString()}`, 'Price']}
                      />
                      <Line type="monotone" dataKey="price" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center">
                    <p className="text-muted-foreground">No chart data available</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Selected Crypto Details */}
            {selectedData && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    {selectedData.name} ({selectedData.symbol})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Price</p>
                      <p className="text-2xl font-bold">${selectedData.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Market Cap</p>
                      <p className="text-xl font-bold">${(selectedData.marketCap / 1e9).toFixed(2)}B</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">24h Volume</p>
                      <p className="text-xl font-bold">${(selectedData.volume24h / 1e6).toFixed(2)}M</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">24h Change</p>
                      <p className={`text-xl font-bold ${selectedData.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {selectedData.change24h >= 0 ? '+' : ''}{selectedData.change24h?.toFixed(2)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">24h High</p>
                      <p className="text-lg font-bold">${selectedData.high24h?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">24h Low</p>
                      <p className="text-lg font-bold">${selectedData.low24h?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Circulating Supply</p>
                      <p className="text-lg font-bold">{selectedData.circulatingSupply?.toLocaleString(undefined, { maximumFractionDigits: 0 })} {selectedData.symbol}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">7d Change</p>
                      <p className={`text-lg font-bold ${selectedData.change7d >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {selectedData.change7d >= 0 ? '+' : ''}{selectedData.change7d?.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Investment Thesis Section */}
        <Card className="border-blue-500/30 bg-blue-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-3 text-blue-400">
              <Lightbulb className="h-6 w-6" />
              AI Investment Thesis
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Bitcoin Thesis */}
              <div className="space-y-2">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                  Bitcoin (BTC)
                </h3>
                <div className="text-sm text-muted-foreground space-y-2">
                  <p><strong className="text-foreground">Thesis:</strong> Digital gold narrative strengthening amid institutional adoption. ETF inflows and halving cycle dynamics support bullish outlook.</p>
                  <p><strong className="text-foreground">Key Metrics:</strong> Market dominance ~50%, hash rate at ATH, long-term holder supply increasing.</p>
                  <p><strong className="text-foreground text-green-500">Bullish</strong> if: Breaks $72K resistance. <strong className="text-foreground text-red-500">Bearish</strong> if: Loses $65K support.</p>
                </div>
              </div>

              {/* Ethereum Thesis */}
              <div className="space-y-2">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                  Ethereum (ETH)
                </h3>
                <div className="text-sm text-muted-foreground space-y-2">
                  <p><strong className="text-foreground">Thesis:</strong> Deflationary tokenomics post-merge. Layer 2 scaling driving adoption. DeFi and NFT ecosystem remains dominant.</p>
                  <p><strong className="text-foreground">Key Metrics:</strong> Staking yield ~3-4%, L2 TVL growing, gas fees stable.</p>
                  <p><strong className="text-foreground text-green-500">Bullish</strong> if: ETH/BTC ratio rebounds. <strong className="text-foreground text-red-500">Bearish</strong> if: L2 competition intensifies.</p>
                </div>
              </div>

              {/* Market Overview Thesis */}
              <div className="space-y-2">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                  Overall Market
                </h3>
                <div className="text-sm text-muted-foreground space-y-2">
                  <p><strong className="text-foreground">Thesis:</strong> Post-halving consolidation phase. Institutional interest growing. Macro headwinds (rates, DXY) remain key risk.</p>
                  <p><strong className="text-foreground">Key Metrics:</strong> Total market cap ${(totalMarketCap / 1e12).toFixed(2)}T, dominance shifting, altseason pending.</p>
                  <p><strong className="text-foreground text-yellow-500">Neutral</strong> - Wait for BTC direction before altcoin exposure.</p>
                </div>
              </div>
            </div>

            <div className="border-t border-blue-500/20 pt-4 mt-4">
              <p className="text-xs text-muted-foreground">
                <strong>Disclaimer:</strong> This is not financial advice. Cryptocurrency investments are highly volatile and risky. Always do your own research (DYOR) and never invest more than you can afford to lose. Data sourced from CoinGecko API.
              </p>
            </div>
          </CardContent>
        </Card>
      </main>

      {/* Footer */}
      <footer className="border-t mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p>Katsu Finance Crypto Dashboard • Powered by CoinGecko API</p>
            <p className="mt-1">Data updated every 2 minutes • For educational purposes only</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
