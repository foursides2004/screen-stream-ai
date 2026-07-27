'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';

interface StreamMessage {
  type: 'analysis' | 'connected' | 'ping' | 'error';
  content?: string;
  timestamp?: string;
  isComplete?: boolean;
}

interface AnalysisMessage {
  id: string;
  timestamp: Date;
  content: string;
  isComplete: boolean;
}

interface CodeBlock {
  type: 'code';
  language: string;
  content: string;
}

interface TextBlock {
  type: 'text';
  content: string;
}

type ContentBlock = CodeBlock | TextBlock;

function parseMarkdown(text: string): ContentBlock[] {
  const blocks: ContentBlock[] = [];
  const codeRegex = /```(\w+)?\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = codeRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      blocks.push({
        type: 'text',
        content: text.slice(lastIndex, match.index),
      });
    }
    blocks.push({
      type: 'code',
      language: match[1] || '',
      content: (match[2] || '').trim(),
    });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    blocks.push({
      type: 'text',
      content: text.slice(lastIndex),
    });
  }

  return blocks;
}

function formatInlineMarkdown(text: string): React.ReactNode {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g).filter(Boolean);
  return (
    <span>
      {parts.map((part, index) => {
        if (part.startsWith('`') && part.endsWith('`')) {
          return <code key={index} className="prose-code">{part.slice(1, -1)}</code>;
        }
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={index}>{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith('*') && part.endsWith('*')) {
          return <em key={index}>{part.slice(1, -1)}</em>;
        }
        return part.split('\n').map((line, i) => (
          <React.Fragment key={i}>
            {line}
            {i < part.split('\n').length - 1 && <br />}
          </React.Fragment>
        ));
      })}
    </span>
  );
}

export default function DashboardPage() {
  const [messages, setMessages] = useState<AnalysisMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [lastCapture, setLastCapture] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const currentMessageRef = useRef<AnalysisMessage | null>(null);
  const latestContentRef = useRef<string>('');

  const connectToStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const es = new EventSource('/api/stream');
    eventSourceRef.current = es;

    es.onopen = () => {
      setIsConnected(true);
      console.log('SSE connected to /api/stream');
    };

    es.onmessage = (event: MessageEvent) => {
      try {
        const data: StreamMessage = JSON.parse(event.data);

        switch (data.type) {
          case 'connected':
            console.log('SSE connected');
            break;

          case 'analysis':
            if (data.content !== undefined) {
              setIsAnalyzing(!data.isComplete);
              latestContentRef.current = data.content;

              if (!currentMessageRef.current || data.isComplete) {
                const newMsg: AnalysisMessage = {
                  id: Date.now().toString(),
                  timestamp: data.timestamp ? new Date(data.timestamp) : new Date(),
                  content: data.content || '',
                  isComplete: data.isComplete || false,
                };
                currentMessageRef.current = newMsg;
                setMessages((prev) => [newMsg, ...prev]);
              } else {
                currentMessageRef.current.content = data.content;
                currentMessageRef.current.isComplete = data.isComplete;
                currentMessageRef.current.timestamp = data.timestamp ? new Date(data.timestamp) : new Date();
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === currentMessageRef.current?.id
                      ? { ...m, content: currentMessageRef.current.content, isComplete: currentMessageRef.current.isComplete }
                      : m
                  )
                );
              }

              if (data.isComplete) {
                setIsAnalyzing(false);
                setLastCapture(new Date().toISOString());
                currentMessageRef.current = null;
              }
            }
            break;

          case 'ping':
            break;

          case 'error':
            console.error('Stream error:', data.content);
            setIsAnalyzing(false);
            currentMessageRef.current = null;
            break;
        }
      } catch (err) {
        console.error('Failed to parse SSE message:', err);
      }
    };

    es.onerror = () => {
      setIsConnected(false);
      setIsAnalyzing(false);
      currentMessageRef.current = null;
      console.error('SSE connection error');
    };
  }, []);

  // Poll /api/latest as fallback for missed updates
  const pollLatest = useCallback(async () => {
    try {
      const res = await fetch('/api/latest');
      if (!res.ok) return;
      const data = await res.json();
      if (data.type === 'analysis' && data.content && data.content !== latestContentRef.current) {
        latestContentRef.current = data.content;
        // If we're not currently streaming, add as new complete message
        if (!isAnalyzing && !currentMessageRef.current) {
          const newMsg: AnalysisMessage = {
            id: Date.now().toString(),
            timestamp: data.timestamp ? new Date(data.timestamp) : new Date(),
            content: data.content,
            isComplete: data.isComplete ?? true,
          };
          setMessages((prev) => [newMsg, ...prev]);
          setLastCapture(new Date().toISOString());
        }
      }
    } catch (e) {
      // Ignore polling errors
    }
  }, [isAnalyzing]);

  useEffect(() => {
    connectToStream();

    // Poll every 2 seconds as fallback
    const interval = setInterval(pollLatest, 2000);

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      clearInterval(interval);
    };
  }, [connectToStream, pollLatest]);

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const formatLastCapture = (iso: string | null): string => {
    if (!iso) return 'Never';
    const date = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderContent = (content: string): React.ReactNode => {
    const blocks = parseMarkdown(content);
    return (
      <div>
        {blocks.map((block, index) => {
          if (block.type === 'code') {
            return (
              <pre key={index} className="bg-muted p-4 rounded-lg overflow-x-auto my-2">
                <code className={`language-${block.language} text-sm font-mono`}>{block.content}</code>
              </pre>
            );
          }
          return (
            <div key={index} className="prose prose-sm dark:prose-invert max-w-none">
              <p>{formatInlineMarkdown(block.content)}</p>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="mx-auto max-w-4xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`} />
              <span className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-background bg-green-500 animate-pulse-soft" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">Screen Stream AI</h1>
              <p className="text-xs text-muted-foreground">
                {isConnected ? 'Live stream active' : 'Connecting...'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full bg-muted ${
              isAnalyzing ? 'animate-pulse-soft' : ''
            }`}>
              <span className="text-muted-foreground">Status:</span>
              <span className="font-medium text-foreground">
                {isAnalyzing ? 'Analyzing...' : 'Waiting for capture'}
              </span>
            </div>

            <div className="hidden sm:block text-right">
              <p className="text-muted-foreground">Last capture</p>
              <p className="font-mono text-foreground">{formatLastCapture(lastCapture)}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 mx-auto max-w-4xl w-full p-4 overflow-auto">
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
              <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-foreground mb-2">Waiting for screen capture</h2>
              <p className="text-muted-foreground max-w-md">
                Press <kbd className="px-2 py-0.5 bg-background border rounded">Ctrl</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">Alt</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">S</kbd> on Windows to capture and analyze your screen.
                The AI response will appear here in real-time.
              </p>
              <div className="mt-6 p-4 bg-muted rounded-lg text-sm text-left max-w-md">
                <p className="font-medium mb-2">Hotkeys (Python client):</p>
                <ol className="space-y-1 text-muted-foreground">
                  <li className="flex items-center gap-2"><kbd className="px-2 py-0.5 bg-background border rounded">Ctrl</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">Alt</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">S</kbd> <span>Capture screen</span></li>
                  <li className="flex items-center gap-2"><kbd className="px-2 py-0.5 bg-background border rounded">Ctrl</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">Alt</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">A</kbd> <span>Toggle auto-capture</span></li>
                  <li className="flex items-center gap-2"><kbd className="px-2 py-0.5 bg-background border rounded">Ctrl</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">Alt</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">M</kbd> <span>Cycle capture mode</span></li>
                  <li className="flex items-center gap-2"><kbd className="px-2 py-0.5 bg-background border rounded">Ctrl</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">Alt</kbd> + <kbd className="px-2 py-0.5 bg-background border rounded">Q</kbd> <span>Quit client</span></li>
                </ol>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <article
                key={msg.id}
                className={`animate-fade-in rounded-xl border border-border bg-card p-6 ${
                  !msg.isComplete ? 'animate-pulse-soft ring-1 ring-primary/20' : ''
                }`}
              >
                <header className="flex items-center justify-between mb-4 pb-3 border-b border-border">
                  <time className="text-xs text-muted-foreground font-mono">
                    {formatTime(msg.timestamp)}
                  </time>
                  {!msg.isComplete && (
                    <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full font-medium">
                      Streaming...
                    </span>
                  )}
                </header>
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  {renderContent(msg.content)}
                </div>
              </article>
            ))
          )}
        </div>

        <div className="h-8" />
      </main>

      <footer className="border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 py-3 px-4">
        <div className="mx-auto max-w-4xl flex items-center justify-between text-xs text-muted-foreground">
          <span>Screen Stream AI Assistant — Localhost Development</span>
          <span className="font-mono">Next.js 15 + OpenRouter</span>
        </div>
      </footer>
    </div>
  );
}