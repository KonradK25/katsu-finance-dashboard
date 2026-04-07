'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Newspaper, TrendingUp, BarChart3 } from 'lucide-react';

interface NewsItem {
  title: string;
  summary?: string;
  url?: string;
  time_published?: string;
  source?: string;
  sentiment_score?: number;
  category?: string;
}

interface NewsFeedProps {
  news: NewsItem[];
}

export function NewsFeed({ news }: NewsFeedProps) {
  if (!news || news.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            Financial News
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">No news available</p>
        </CardContent>
      </Card>
    );
  }

  const getSentimentColor = (score?: number) => {
    if (!score) return 'text-gray-500';
    if (score > 0.1) return 'text-green-500';
    if (score < -0.1) return 'text-red-500';
    return 'text-yellow-500';
  };

  const getSentimentLabel = (score?: number) => {
    if (!score) return 'Neutral';
    if (score > 0.1) return 'Bullish';
    if (score < -0.1) return 'Bearish';
    return 'Neutral';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Newspaper className="h-5 w-5" />
          Financial News & Sentiment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {news.slice(0, 10).map((item, index) => (
            <div
              key={index}
              className="border-b border-border pb-4 last:border-0 last:pb-0"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-sm">{item.title}</h4>
                    {item.source && (
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        item.source === 'FRED' 
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                          : item.source === 'BEA'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                      }`}>
                        {item.source}
                      </span>
                    )}
                    {item.category && (
                      <span className="text-xs text-muted-foreground">
                        {item.category}
                      </span>
                    )}
                  </div>
                  {item.summary && (
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {item.summary}
                    </p>
                  )}
                  <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                    {item.source && <span>{item.source}</span>}
                    {item.time_published && (
                      <span>
                        {new Date(item.time_published).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit'
                        })}
                      </span>
                    )}
                  </div>
                </div>
                <div className={`text-xs font-medium ${getSentimentColor(item.sentiment_score)}`}>
                  {getSentimentLabel(item.sentiment_score)}
                </div>
              </div>
              {item.url && (
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary hover:underline mt-2 inline-block"
                >
                  Read more →
                </a>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
