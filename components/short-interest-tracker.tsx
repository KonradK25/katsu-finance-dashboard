'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingDown, 
  TrendingUp, 
  AlertTriangle, 
  Shield, 
  RefreshCw,
  ExternalLink,
  Info
} from 'lucide-react';

interface ShortInterestData {
  symbol: string;
  companyName: string;
  shortInterest: number;
  previousShortInterest: number;
  changePercent: number;
  avgDailyVolume: number;
  daysTocover: number;
  shortPercentOfFloat: number;
  settlementDate: string;
  previousSettlementDate: string;
  squeezeRisk?: {
    score: number;
    level: string;
    color: string;
  };
}

export function ShortInterestTracker() {
  const [data, setData] = useState<ShortInterestData[]>([]);
  const [loading, setLoading] = useState(false);
  const [sortBy, setSortBy] = useState<'daysTocover' | 'shortPercent' | 'change'>('daysTocover');

  const fetchShortInterest = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/short-interest?squeeze=true');
      const result = await res.json();
      
      if (result.success) {
        setData(result.data);
      }
    } catch (error) {
      console.error('Error fetching short interest:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShortInterest();
  }, []);

  const formatNumber = (num: number) => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
    return num.toString();
  };

  const getChangeColor = (change: number) => {
    if (change > 5) return 'text-red-500';
    if (change > 0) return 'text-orange-500';
    if (change > -5) return 'text-blue-500';
    return 'text-green-500';
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="h-3 w-3" />;
    if (change < 0) return <TrendingDown className="h-3 w-3" />;
    return null;
  };

  const sortedData = [...data].sort((a, b) => {
    switch (sortBy) {
      case 'daysTocover':
        return b.daysTocover - a.daysTocover;
      case 'shortPercent':
        return b.shortPercentOfFloat - a.shortPercentOfFloat;
      case 'change':
        return b.changePercent - a.changePercent;
      default:
        return 0;
    }
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            <span>Short Interest & Squeeze Risk</span>
          </div>
          <button
            onClick={fetchShortInterest}
            disabled={loading}
            className="inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-8 rounded-md px-3 text-xs gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Info Banner */}
        <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-sm">
          <Info className="h-4 w-4 text-blue-500 mt-0.5" />
          <div className="text-blue-500">
            <p className="font-semibold mb-1">Understanding Short Interest</p>
            <ul className="text-xs space-y-1 text-blue-400">
              <li>• <strong>Days to Cover:</strong> How many days to buy back all shorts (higher = more squeeze potential)</li>
              <li>• <strong>Short % of Float:</strong> Percentage of tradable shares sold short</li>
              <li>• <strong>Change:</strong> Increase in short interest (red = more shorts, green = covering)</li>
            </ul>
          </div>
        </div>

        {/* Sort Buttons */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setSortBy('daysTocover')}
            className={`inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border h-8 rounded-md px-3 text-xs gap-2 ${
              sortBy === 'daysTocover' 
                ? 'bg-primary text-primary-foreground' 
                : 'border-input bg-background hover:bg-accent'
            }`}
          >
            Sort by Days to Cover
          </button>
          <button
            onClick={() => setSortBy('shortPercent')}
            className={`inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity:opacity-50 border h-8 rounded-md px-3 text-xs gap-2 ${
              sortBy === 'shortPercent' 
                ? 'bg-primary text-primary-foreground' 
                : 'border-input bg-background hover:bg-accent'
            }`}
          >
            Sort by Short % Float
          </button>
          <button
            onClick={() => setSortBy('change')}
            className={`inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border h-8 rounded-md px-3 text-xs gap-2 ${
              sortBy === 'change' 
                ? 'bg-primary text-primary-foreground' 
                : 'border-input bg-background hover:bg-accent'
            }`}
          >
            Sort by Change %
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
            <p className="text-muted-foreground">Loading short interest data...</p>
          </div>
        )}

        {/* Short Interest Table */}
        {!loading && data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-muted-foreground">
                  <th className="text-left py-3 px-2 font-medium">Symbol</th>
                  <th className="text-right py-3 px-2 font-medium">Short Interest</th>
                  <th className="text-right py-3 px-2 font-medium">% Float</th>
                  <th className="text-right py-3 px-2 font-medium">Days to Cover</th>
                  <th className="text-right py-3 px-2 font-medium">Change</th>
                  <th className="text-center py-3 px-2 font-medium">Squeeze Risk</th>
                </tr>
              </thead>
              <tbody>
                {sortedData.map((item) => (
                  <tr key={item.symbol} className="border-b hover:bg-muted/30 transition-colors">
                    <td className="py-3 px-2">
                      <div>
                        <span className="font-semibold">{item.symbol}</span>
                        <div className="text-xs text-muted-foreground">{item.companyName}</div>
                      </div>
                    </td>
                    <td className="text-right py-3 px-2">
                      <div className="font-medium">{formatNumber(item.shortInterest)}</div>
                      <div className="text-xs text-muted-foreground">
                        Vol: {formatNumber(item.avgDailyVolume)}
                      </div>
                    </td>
                    <td className="text-right py-3 px-2">
                      <span className={`font-semibold ${
                        item.shortPercentOfFloat > 10 ? 'text-red-500' : 
                        item.shortPercentOfFloat > 5 ? 'text-orange-500' : 'text-green-500'
                      }`}>
                        {item.shortPercentOfFloat.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-right py-3 px-2">
                      <span className={`font-semibold ${
                        item.daysTocover > 5 ? 'text-red-500' : 
                        item.daysTocover > 3 ? 'text-orange-500' : 'text-green-500'
                      }`}>
                        {item.daysTocover.toFixed(1)}
                      </span>
                    </td>
                    <td className="text-right py-3 px-2">
                      <div className={`flex items-center justify-end gap-1 ${getChangeColor(item.changePercent)}`}>
                        {getChangeIcon(item.changePercent)}
                        <span className="font-medium">{item.changePercent > 0 ? '+' : ''}{item.changePercent.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="text-center py-3 px-2">
                      {item.squeezeRisk && (
                        <Badge className={`${item.squeezeRisk.color} border`}>
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          {item.squeezeRisk.level}
                        </Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Empty State */}
        {!loading && data.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <Shield className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>No short interest data available</p>
          </div>
        )}

        {/* Footer Note */}
        <div className="text-xs text-muted-foreground pt-4 border-t">
          <p>Data source: FINRA (published twice monthly)</p>
          <p>Last settlement: {data[0]?.settlementDate || 'N/A'}</p>
        </div>
      </CardContent>
    </Card>
  );
}
