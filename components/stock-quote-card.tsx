'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, DollarSign, Percent } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StockQuoteCardProps {
  symbol: string;
  data: any;
}

export function StockQuoteCard({ symbol, data }: StockQuoteCardProps) {
  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{symbol}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  const price = parseFloat(data['05. price'] || 0);
  const change = parseFloat(data['09. change'] || 0);
  const changePercent = parseFloat(data['10. change percent'] || 0);
  const volume = parseInt(data['06. volume'] || 0);
  const previousClose = parseFloat(data['08. previous close'] || 0);

  const isPositive = change >= 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-2xl font-bold">{symbol}</CardTitle>
        {isPositive ? (
          <TrendingUp className="h-5 w-5 text-green-500" />
        ) : (
          <TrendingDown className="h-5 w-5 text-red-500" />
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="text-3xl font-bold">${price.toFixed(2)}</div>
          <div className={cn(
            'flex items-center text-sm',
            isPositive ? 'text-green-500' : 'text-red-500'
          )}>
            {isPositive ? '+' : ''}{change.toFixed(2)} ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
          </div>
          <div className="grid grid-cols-2 gap-2 pt-2 text-xs text-muted-foreground">
            <div className="flex items-center">
              <DollarSign className="h-3 w-3 mr-1" />
              Prev: ${previousClose.toFixed(2)}
            </div>
            <div className="flex items-center">
              <Percent className="h-3 w-3 mr-1" />
              Vol: {(volume / 1e6).toFixed(1)}M
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
