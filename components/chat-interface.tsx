'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Send, BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Hey! I'm Katsu, your finance assistant. Ask me anything about stocks, market trends, economic data, or investment strategies. What's on your mind?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // TODO: Connect to OpenClaw API for real responses
    // For now, simulate a response
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: "Thanks for your question! In the full version, I'll connect to OpenClaw to provide detailed financial analysis, market insights, and investment recommendations. For now, try searching for a stock symbol in the search bar above!",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Send className="h-5 w-5" />
          Chat with Katsu
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg p-3">
                <p className="text-sm text-muted-foreground">Thinking...</p>
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about stocks, market trends, or investment strategies..."
            disabled={isLoading}
          />
          <Button onClick={handleSend} disabled={isLoading || !input.trim()} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground mb-2">Quick questions:</p>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setInput("What's the current market outlook?")}
              className="text-xs"
            >
              <BarChart3 className="h-3 w-3 mr-1" />
              Market Outlook
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setInput("Analyze AAPL stock")}
              className="text-xs"
            >
              <TrendingUp className="h-3 w-3 mr-1" />
              Analyze AAPL
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setInput("What are the risks in the current market?")}
              className="text-xs"
            >
              <AlertTriangle className="h-3 w-3 mr-1" />
              Market Risks
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
