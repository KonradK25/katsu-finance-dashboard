'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Newspaper, TrendingUp, Globe, Shield, DollarSign, BarChart3, ExternalLink, RefreshCw } from 'lucide-react';

interface NewsItem {
  title: string;
  summary: string;
  url: string;
  time_published: string;
  source: string;
  sourceColor: string;
  category: string;
}

interface MarketUpdatesProps {
  onNewsLoad?: (news: NewsItem[]) => void;
  news?: NewsItem[];
}

const CATEGORIES = [
  {
    id: 'macro',
    name: 'Macroeconomic News',
    icon: DollarSign,
    color: 'bg-blue-600',
    searchQuery: 'Federal Reserve interest rates inflation GDP'
  },
  {
    id: 'geopolitics',
    name: 'Iran & Geopolitical Conflict',
    icon: Shield,
    color: 'bg-red-600',
    searchQuery: 'Iran Middle East conflict oil prices tensions'
  },
  {
    id: 'markets',
    name: 'Stock Market Updates',
    icon: BarChart3,
    color: 'bg-green-600',
    searchQuery: 'S&P 500 Dow Jones stock market rally decline'
  },
  {
    id: 'global',
    name: 'Global Economy',
    icon: Globe,
    color: 'bg-purple-600',
    searchQuery: 'China Europe economy trade markets growth'
  }
];

export function MarketUpdates({ onNewsLoad }: MarketUpdatesProps) {
  const [loading, setLoading] = useState(false);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const generateMarketUpdates = async () => {
    setLoading(true);
    try {
      // Fetch general news
      const res = await fetch('/api/news');
      const allNews = await res.json();

      // Categorize news into 4 topics
      const categorizedNews: NewsItem[] = [];

      for (const category of CATEGORIES) {
        // Filter news related to this category
        const keywords = category.searchQuery.toLowerCase().split(' ');
        const relevantNews = allNews.filter((item: NewsItem) => {
          const text = (item.title + ' ' + item.summary).toLowerCase();
          return keywords.some(keyword => text.includes(keyword));
        });

        // Pick the best article for this category
        if (relevantNews.length > 0) {
          categorizedNews.push({
            ...relevantNews[0],
            category: category.name
          });
        } else {
          // Fallback: use first available news with category tag
          const fallback = allNews[categorizedNews.length % allNews.length];
          if (fallback) {
            categorizedNews.push({
              ...fallback,
              category: category.name
            });
          }
        }
      }

      setNews(categorizedNews);
      setLastUpdated(new Date());
      
      if (onNewsLoad) {
        onNewsLoad(categorizedNews);
      }
    } catch (error) {
      console.error('Error generating market updates:', error);
    } finally {
      setLoading(false);
    }
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

  const getSourceBadgeStyle = (source: string) => {
    const sourceUpper = source.toUpperCase();
    if (sourceUpper === 'CNBC') return 'bg-red-600 text-white';
    if (sourceUpper === 'BLOOMBERG') return 'bg-blue-600 text-white';
    if (sourceUpper === 'WSJ' || sourceUpper === 'WALL STREET JOURNAL') return 'bg-gray-900 text-white';
    if (sourceUpper === 'FRED') return 'bg-blue-500 text-white';
    if (sourceUpper === 'BEA') return 'bg-green-500 text-white';
    if (sourceUpper === 'REUTERS') return 'bg-orange-500 text-white';
    return 'bg-gray-600 text-white';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            <span>Market Updates</span>
          </div>
          {lastUpdated && (
            <span className="text-xs text-muted-foreground">
              Updated {formatTimeAgo(lastUpdated.toISOString())}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {!news.length && !loading && (
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">
              Click below to generate today's key market updates
            </p>
            <Button 
              onClick={generateMarketUpdates}
              className="gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Generate Market Updates
            </Button>
          </div>
        )}

        {loading && (
          <div className="text-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
            <p className="text-muted-foreground">Fetching latest updates...</p>
          </div>
        )}

        {news.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {news.map((item, index) => {
                const IconComponent = CATEGORIES.find(c => c.name === item.category)?.icon || Newspaper;
                const categoryColor = CATEGORIES.find(c => c.name === item.category)?.color || 'bg-gray-600';
                
                return (
                  <div
                    key={index}
                    className="border border-border rounded-lg p-4 hover:bg-muted/30 transition-all"
                  >
                    <div className="flex items-start gap-3 mb-2">
                      <div className={`p-2 rounded-lg ${categoryColor}`}>
                        <IconComponent className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="font-semibold text-sm line-clamp-2">
                            {item.title}
                          </h4>
                          {item.source && (
                            <span className={`text-xs px-2 py-1 rounded-full whitespace-nowrap ${getSourceBadgeStyle(item.source)}`}>
                              {item.source}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                          {item.summary}
                        </p>
                        <div className="flex items-center gap-2 mt-2 text-xs">
                          <span className="text-muted-foreground">
                            {formatTimeAgo(item.time_published)}
                          </span>
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
                );
              })}
            </div>

            <div className="flex justify-center pt-2">
              <Button 
                variant="outline" 
                onClick={generateMarketUpdates}
                disabled={loading}
                className="gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh Updates
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
