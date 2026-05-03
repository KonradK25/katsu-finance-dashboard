'use client';

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface StockChartProps {
  data: any[];
  title?: string;
  symbol?: string;
}

export function StockChart({ data, title = 'Price History', symbol }: StockChartProps) {
  console.log('StockChart received:', { dataLength: data?.length, data });
  
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{symbol ? `${symbol} - ${title}` : title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-2">Chart data unavailable</p>
            <p className="text-xs text-muted-foreground">
              Data length: {data?.length || 0}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const chartData = data.map((item: any) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    price: parseFloat(item.close || item.value || 0)
  })).reverse().slice(-30); // Last 30 data points

  return (
    <Card>
      <CardHeader>
        <CardTitle>{symbol ? `${symbol} - ${title}` : title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <XAxis
              dataKey="date"
              stroke="#888888"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#888888"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--background))',
                border: '1px solid hsl(var(--border))',
                borderRadius: 'var(--radius)'
              }}
              formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Price']}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
