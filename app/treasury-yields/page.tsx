'use client';

import { useEffect, useState } from 'react';
import { ArrowLeft, TrendingUp, Shield } from 'lucide-react';
import Link from 'next/link';
import { ShortInterestTracker } from '@/components/short-interest-tracker';

interface YieldCurveData {
  yields: Record<string, { value: number | null; date: string }>;
  spreads: {
    '10Y-2Y': number | null;
    '10Y-3MO': number | null;
    '30Y-5Y': number | null;
  };
  curveStatus: {
    status: string;
    isInverted: boolean;
    isNormal: boolean;
  };
  lastUpdated: string;
}

export default function TreasuryYieldCurve() {
  const [data, setData] = useState<YieldCurveData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    fetch('/api/treasury-yields', { signal: controller.signal })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(result => {
        setData(result);
      })
      .catch(err => {
        if (err.name === 'AbortError') {
          setError('Request timed out');
        } else {
          setError(err.message);
        }
      })
      .finally(() => {
        clearTimeout(timeoutId);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">Treasury Yield Curve</h1>
                <p className="text-sm text-muted-foreground">Real-time U.S. Treasury yields from FRED</p>
              </div>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-2 text-muted-foreground animate-pulse">
            Loading yield data...
          </div>
        </main>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">Treasury Yield Curve</h1>
                <p className="text-sm text-muted-foreground">Real-time U.S. Treasury yields from FRED</p>
              </div>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="bg-destructive/15 border border-destructive rounded-lg p-4">
            <p className="text-destructive font-semibold">Error loading data</p>
            <p className="text-muted-foreground text-sm mt-2">{error || 'Unknown error'}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-md"
            >
              Retry
            </button>
          </div>
        </main>
      </div>
    );
  }

  const getStatusColor = () => {
    if (data.curveStatus.isInverted) return 'text-red-500 bg-red-500/10 border-red-500/20';
    if (data.curveStatus.isNormal) return 'text-green-500 bg-green-500/10 border-green-500/20';
    return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
  };

  const getSpreadColor = (value: number | null) => {
    if (value === null) return 'text-muted-foreground';
    return value < 0 ? 'text-red-500' : 'text-green-500';
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">Treasury Yield Curve</h1>
                <p className="text-sm text-muted-foreground">Real-time U.S. Treasury yields from FRED</p>
              </div>
            </div>
            <Link href="/">
              <button className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-6">
        {/* Status Badge */}
        <div className="flex items-center gap-4">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border ${getStatusColor()}`}>
            <div className={`w-2 h-2 rounded-full ${
              data.curveStatus.isInverted ? 'bg-red-500' : data.curveStatus.isNormal ? 'bg-green-500' : 'bg-yellow-500'
            }`} />
            <span className="font-semibold">{data.curveStatus.status.toUpperCase()} CURVE</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Last updated: {data.lastUpdated}
          </p>
        </div>

        {/* Key Spreads */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card">
            <div className="p-6">
              <p className="text-sm text-muted-foreground mb-2">10Y - 2Y Spread</p>
              <p className={`text-3xl font-bold ${getSpreadColor(data.spreads['10Y-2Y'])}`}>
                {data.spreads['10Y-2Y']?.toFixed(2) || 'N/A'}%
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                {data.spreads['10Y-2Y']! < 0 ? '⚠️ Inverted' : '✓ Normal'}
              </p>
            </div>
          </div>
          <div className="card">
            <div className="p-6">
              <p className="text-sm text-muted-foreground mb-2">10Y - 3MO Spread</p>
              <p className={`text-3xl font-bold ${getSpreadColor(data.spreads['10Y-3MO'])}`}>
                {data.spreads['10Y-3MO']?.toFixed(2) || 'N/A'}%
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                {data.spreads['10Y-3MO']! < 0 ? '⚠️ Inverted' : '✓ Normal'}
              </p>
            </div>
          </div>
          <div className="card">
            <div className="p-6">
              <p className="text-sm text-muted-foreground mb-2">30Y - 5Y Spread</p>
              <p className="text-3xl font-bold text-green-500">
                {data.spreads['30Y-5Y']?.toFixed(2) || 'N/A'}%
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                Long-term term premium
              </p>
            </div>
          </div>
        </div>

        {/* Yields Grid */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-6">Current Yields by Maturity</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {Object.entries(data.yields).map(([maturity, { value, date }]) => (
                <div key={maturity} className="text-center p-4 rounded-lg bg-muted/50">
                  <p className="text-sm font-medium text-muted-foreground mb-2">{maturity}</p>
                  <p className="text-2xl font-bold text-primary">
                    {value?.toFixed(2) || 'N/A'}%
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">{date}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Short Interest Tracker */}
        <section>
          <ShortInterestTracker />
        </section>

        {/* Educational Info */}
        <div className="rounded-lg border bg-muted/50 p-6">
          <h3 className="font-semibold mb-3">📚 Understanding the Yield Curve</h3>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>
              <span className="text-green-500 font-medium">Normal Curve:</span> Long-term rates are higher than short-term rates, indicating expectations of economic growth.
            </p>
            <p>
              <span className="text-yellow-500 font-medium">Flattening:</span> The spread between long and short-term rates is narrowing, signaling economic uncertainty.
            </p>
            <p>
              <span className="text-red-500 font-medium">Inverted Curve:</span> Short-term rates exceed long-term rates. This has preceded every U.S. recession since 1955, typically occurring 12-18 months before the downturn.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
