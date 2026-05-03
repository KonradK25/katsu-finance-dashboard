'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Newspaper, TrendingUp, BarChart3, ExternalLink } from 'lucide-react';

interface NewsItem {
  title: string;
  summary?: string;
  url?: string;
  time_published?: string;
  source?: string;
  sourceColor?: string;
  sentiment_score?: number;
  category?: string;
  image?: string;
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

  const getSourceBadgeStyle = (source: string) => {
    const sourceUpper = source.toUpperCase();
    if (sourceUpper === 'CNBC') return 'bg-red-600 text-white';
    if (sourceUpper === 'BLOOMBERG') return 'bg-blue-600 text-white';
    if (sourceUpper === 'WSJ' || sourceUpper === 'WALL STREET JOURNAL') return 'bg-gray-900 text-white';
    if (sourceUpper === 'FRED') return 'bg-blue-500 text-white';
    if (sourceUpper === 'BEA') return 'bg-green-500 text-white';
    if (sourceUpper === 'REUTERS') return 'bg-orange-500 text-white';
    if (sourceUpper === 'YAHOO FINANCE') return 'bg-purple-500 text-white';
    return 'bg-gray-600 text-white';
  };

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

  const formatTimeAgo = (timestamp?: string) => {
    if (!timestamp) return '';
    const now = Date.now();
    const then = new Date(timestamp).getTime();
    const diff = now - then;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            <span>Financial News</span>
          </div>
          <span className="text-xs text-muted-foreground">
            Live from CNBC, Bloomberg, WSJ
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
          {news.slice(0, 15).map((item, index) => (
            <div
              key={index}
              className="border border-border rounded-lg p-3 hover:bg-muted/30 transition-all"
            >
              <div className="flex items-start gap-3">
                {item.image && (
                  <img 
                    src={item.image} 
                    alt="" 
                    className="w-16 h-16 object-cover rounded-md flex-shrink-0"
                    onError={(e) => (e.currentTarget.style.display = 'none')}
                  />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <h4 className="font-semibold text-sm line-clamp-2 flex-1">
                      {item.title}
                    </h4>
                    {item.source && (
                      <span className={`text-xs px-2 py-1 rounded-full whitespace-nowrap ${getSourceBadgeStyle(item.source)}`}>
                        {item.source}
                      </span>
                    )}
                  </div>
                  {item.summary && (
                    <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                      {item.summary}
                    </p>
                  )}
                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-muted-foreground">
                      {formatTimeAgo(item.time_published)}
                    </span>
                    {item.sentiment_score !== undefined && (
                      <span className={`font-medium ${getSentimentColor(item.sentiment_score)}`}>
                        {getSentimentLabel(item.sentiment_score)}
                      </span>
                    )}
                    {item.url && (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline flex items-center gap-1"
                      >
                        <span>Read more</span>
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
