'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import Link from 'next/link';

interface AnswerChoice {
  label: string;
  content: string;
}

interface QuestionEntry {
  id: string;
  question: string;
  choices: AnswerChoice[];
  correctAnswer: string[];
  domain: string;
  seenCount: number;
  lastSeenAt: string;
  createdAt: string;
}

interface StreamMessage {
  type: 'qa_entry';
  entry?: QuestionEntry;
  timestamp?: string;
}

export default function ReviewerPage() {
  const [entries, setEntries] = useState<QuestionEntry[]>([]);
  const [search, setSearch] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const eventSourceRef = useRef<EventSource | null>(null);

  const fetchEntries = useCallback(async () => {
    try {
      const res = await fetch('/api/reviewer/entries');
      const data = await res.json();
      setEntries(data.entries || []);
    } catch (err) {
      console.error('Failed to fetch reviewer entries:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEntries();

    const es = new EventSource('/api/stream');
    eventSourceRef.current = es;

    es.onmessage = (event: MessageEvent) => {
      try {
        const data: StreamMessage = JSON.parse(event.data);
        if (data.type === 'qa_entry' && data.entry) {
          setEntries((prev) => {
            const existing = prev.find((e) => e.id === data.entry!.id);
            if (existing) {
              return prev.map((e) => (e.id === data.entry!.id ? data.entry! : e));
            }
            return [data.entry!, ...prev];
          });
        }
      } catch {
        // ignore parse errors
      }
    };

    return () => {
      es.close();
    };
  }, [fetchEntries]);

  const domains = Array.from(new Set(entries.map((e) => e.domain).filter(Boolean))).sort();

  const filtered = entries.filter((e) => {
    const matchesSearch =
      !search ||
      e.question.toLowerCase().includes(search.toLowerCase()) ||
      e.choices.some((c) => c.content.toLowerCase().includes(search.toLowerCase()));
    const matchesDomain = !domainFilter || e.domain === domainFilter;
    return matchesSearch && matchesDomain;
  });

  const formatTime = (iso: string): string => {
    const date = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  const handleDelete = useCallback(async (id: string) => {
    try {
      await fetch('/api/reviewer/entries', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id }),
      });
      setEntries((prev) => prev.filter((e) => e.id !== id));
    } catch (err) {
      console.error('Failed to delete entry:', err);
    }
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="mx-auto max-w-4xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Dashboard
            </Link>
            <div>
              <h1 className="text-lg font-semibold text-foreground">Reviewer</h1>
              <p className="text-xs text-muted-foreground">
                {entries.length} question{entries.length !== 1 ? 's' : ''} stored
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 mx-auto max-w-4xl w-full p-4 overflow-auto">
        {/* Search and Filter */}
        <div className="flex gap-3 mb-4">
          <input
            type="text"
            placeholder="Search questions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          {domains.length > 0 && (
            <select
              value={domainFilter}
              onChange={(e) => setDomainFilter(e.target.value)}
              className="px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">All domains</option>
              {domains.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Entries */}
        {loading ? (
          <div className="flex items-center justify-center min-h-[40vh]">
            <p className="text-muted-foreground">Loading...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-foreground mb-2">
              {entries.length === 0 ? 'No questions yet' : 'No matching questions'}
            </h2>
            <p className="text-muted-foreground max-w-md">
              {entries.length === 0
                ? 'Capture a screen with a question to start building your reviewer.'
                : 'Try a different search term or domain filter.'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filtered.map((entry) => (
              <article
                key={entry.id}
                className="rounded-xl border border-border bg-card p-6 animate-fade-in"
              >
                <header className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-foreground font-medium leading-relaxed">
                      {entry.question}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2 ml-4 shrink-0">
                    {entry.domain && (
                      <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full font-medium">
                        {entry.domain}
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground">
                      ×{entry.seenCount}
                    </span>
                  </div>
                </header>

                {entry.choices.length > 0 && (
                  <div className="space-y-1.5 mb-3">
                    {entry.choices.map((choice) => {
                      const isCorrect = entry.correctAnswer.includes(choice.label);
                      return (
                        <div
                          key={choice.label}
                          className={`flex items-start gap-2 px-3 py-2 rounded-lg text-sm ${
                            isCorrect
                              ? 'bg-green-500/10 border border-green-500/20 text-green-700 dark:text-green-400'
                              : 'bg-muted text-muted-foreground'
                          }`}
                        >
                          <span className="font-mono font-medium shrink-0 w-5">
                            {choice.label}.
                          </span>
                          <span>{choice.content}</span>
                          {isCorrect && (
                            <span className="ml-auto shrink-0">✓</span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {entry.choices.length === 0 && (
                  <div className="px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/20 text-sm text-green-700 dark:text-green-400 mb-3">
                    Answer: {entry.correctAnswer.join(', ')}
                  </div>
                )}

                <footer className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Last seen {formatTime(entry.lastSeenAt)}</span>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="text-xs text-muted-foreground hover:text-red-500 transition-colors px-2 py-1 rounded hover:bg-red-500/10"
                  >
                    Delete
                  </button>
                </footer>
              </article>
            ))}
          </div>
        )}
      </main>

      <footer className="border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 py-3 px-4">
        <div className="mx-auto max-w-4xl flex items-center justify-between text-xs text-muted-foreground">
          <span>Screen Stream AI — Reviewer</span>
          <span className="font-mono">{filtered.length} / {entries.length} shown</span>
        </div>
      </footer>
    </div>
  );
}
