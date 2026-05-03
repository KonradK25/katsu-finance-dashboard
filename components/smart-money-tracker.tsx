'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  User, 
  DollarSign, 
  Building, 
  FileText, 
  ExternalLink,
  RefreshCw,
  Shield,
  Award,
  Briefcase
} from 'lucide-react';

interface InsiderTrade {
  ticker: string;
  companyName: string;
  insiderName: string;
  title: string;
  transactionType: 'P' | 'S' | 'A' | 'M';
  shares: number;
  pricePerShare: number;
  totalValue: number;
  sharesOwned: number;
  filingDate: string;
  transactionDate: string;
  formType: string;
  secUrl: string;
}

interface SmartMoneyStats {
  totalTrades: number;
  totalBuyValue: number;
  totalSellValue: number;
  buySellRatio: number;
  topBoughtTicker: string;
  topSoldTicker: string;
}

export function SmartMoneyTracker() {
  const [trades, setTrades] = useState<InsiderTrade[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'P' | 'S'>('all');
  const [stats, setStats] = useState<SmartMoneyStats | null>(null);

  const fetchInsiderTrades = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('limit', '50');
      if (filter !== 'all') {
        params.set('type', filter);
      }

      const res = await fetch(`/api/insider-trades?${params.toString()}`);
      const data = await res.json();
      
      if (data.success) {
        setTrades(data.data);
        calculateStats(data.data);
      }
    } catch (error) {
      console.error('Error fetching insider trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (tradeData: InsiderTrade[]) => {
    const buys = tradeData.filter(t => t.transactionType === 'P');
    const sells = tradeData.filter(t => t.transactionType === 'S');
    
    const totalBuyValue = buys.reduce((sum, t) => sum + t.totalValue, 0);
    const totalSellValue = sells.reduce((sum, t) => sum + t.totalValue, 0);
    
    // Group by ticker
    const byTicker: Record<string, { buys: number; sells: number }> = {};
    tradeData.forEach(t => {
      if (!byTicker[t.ticker]) {
        byTicker[t.ticker] = { buys: 0, sells: 0 };
      }
      if (t.transactionType === 'P') {
        byTicker[t.ticker].buys += t.totalValue;
      } else {
        byTicker[t.ticker].sells += t.totalValue;
      }
    });

    // Find top bought and sold
    let topBought = '';
    let topSold = '';
    let maxBuy = 0;
    let maxSell = 0;
    
    Object.entries(byTicker).forEach(([ticker, values]) => {
      if (values.buys > maxBuy) {
        maxBuy = values.buys;
        topBought = ticker;
      }
      if (values.sells > maxSell) {
        maxSell = values.sells;
        topSold = ticker;
      }
    });

    setStats({
      totalTrades: tradeData.length,
      totalBuyValue,
      totalSellValue,
      buySellRatio: totalSellValue > 0 ? totalBuyValue / totalSellValue : 0,
      topBoughtTicker: topBought,
      topSoldTicker: topSold
    });
  };

  useEffect(() => {
    fetchInsiderTrades();
  }, [filter]);

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
    return `$${value.toFixed(2)}`;
  };

  const formatNumber = (num: number) => {
    if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
    return num.toString();
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'P': return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'S': return <TrendingDown className="h-4 w-4 text-red-500" />;
      case 'A': return <Award className="h-4 w-4 text-blue-500" />;
      case 'M': return <Briefcase className="h-4 w-4 text-purple-500" />;
      default: return <DollarSign className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTransactionLabel = (type: string) => {
    switch (type) {
      case 'P': return 'Purchase';
      case 'S': return 'Sale';
      case 'A': return 'Award';
      case 'M': return 'Exercise';
      default: return type;
    }
  };

  const getTransactionColor = (type: string) => {
    switch (type) {
      case 'P': return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'S': return 'bg-red-500/10 text-red-500 border-red-500/20';
      case 'A': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'M': return 'bg-purple-500/10 text-purple-500 border-purple-500/20';
      default: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            <span>Smart Money Tracker</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchInsiderTrades}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="p-3 rounded-lg border bg-muted/30">
              <div className="text-xs text-muted-foreground mb-1">Total Trades</div>
              <div className="text-lg font-bold">{stats.totalTrades}</div>
            </div>
            <div className="p-3 rounded-lg border bg-muted/30">
              <div className="text-xs text-muted-foreground mb-1">Insider Buying</div>
              <div className="text-lg font-bold text-green-500">{formatCurrency(stats.totalBuyValue)}</div>
            </div>
            <div className="p-3 rounded-lg border bg-muted/30">
              <div className="text-xs text-muted-foreground mb-1">Insider Selling</div>
              <div className="text-lg font-bold text-red-500">{formatCurrency(stats.totalSellValue)}</div>
            </div>
            <div className="p-3 rounded-lg border bg-muted/30">
              <div className="text-xs text-muted-foreground mb-1">Buy/Sell Ratio</div>
              <div className="text-lg font-bold">{stats.buySellRatio.toFixed(2)}</div>
            </div>
          </div>
        )}

        {/* Filter Buttons */}
        <div className="flex gap-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            All Trades
          </Button>
          <Button
            variant={filter === 'P' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('P')}
          >
            <TrendingUp className="h-3 w-3 mr-1" />
            Purchases
          </Button>
          <Button
            variant={filter === 'S' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('S')}
          >
            <TrendingDown className="h-3 w-3 mr-1" />
            Sales
          </Button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
            <p className="text-muted-foreground">Fetching insider trades...</p>
          </div>
        )}

        {/* Trades List */}
        {!loading && trades.length > 0 && (
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
            {trades.map((trade, index) => (
              <div
                key={index}
                className="border border-border rounded-lg p-4 hover:bg-muted/30 transition-all"
              >
                <div className="flex items-start justify-between gap-3">
                  {/* Left: Ticker & Company */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="secondary" className="font-bold">
                        {trade.ticker}
                      </Badge>
                      <span className="text-sm font-semibold">{trade.companyName}</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                      <User className="h-3 w-3" />
                      <span>{trade.insiderName}</span>
                      <span className="text-xs">•</span>
                      <span className="text-xs">{trade.title}</span>
                    </div>

                    <div className="flex items-center gap-4 text-xs">
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-3 w-3 text-muted-foreground" />
                        <span>{formatNumber(trade.shares)} shares @ ${trade.pricePerShare.toFixed(2)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Building className="h-3 w-3 text-muted-foreground" />
                        <span>Owns: {formatNumber(trade.sharesOwned)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Right: Transaction Details */}
                  <div className="text-right">
                    <Badge className={`mb-2 ${getTransactionColor(trade.transactionType)}`}>
                      {getTransactionIcon(trade.transactionType)}
                      <span className="ml-1">{getTransactionLabel(trade.transactionType)}</span>
                    </Badge>
                    
                    <div className="text-lg font-bold">
                      {formatCurrency(trade.totalValue)}
                    </div>
                    
                    <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                      <FileText className="h-3 w-3" />
                      <span>{formatTimeAgo(trade.filingDate)}</span>
                    </div>

                    <a
                      href={trade.secUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-primary hover:underline mt-1"
                    >
                      <span>View Filing</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && trades.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>No insider trades found</p>
            <p className="text-xs mt-1">Try adjusting your filters</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
