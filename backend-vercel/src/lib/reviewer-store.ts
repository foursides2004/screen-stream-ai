/**
 * In-memory Q&A store for the reviewer feature.
 * Data is ephemeral (lost on Vercel cold start) but re-synced from the Python client.
 */

export interface AnswerChoice {
  label: string;
  content: string;
}

export interface QuestionEntry {
  id: string;
  question: string;
  choices: AnswerChoice[];
  correctAnswer: string[];
  domain: string;
  seenCount: number;
  lastSeenAt: string;
  createdAt: string;
}

function normalizeQuestion(text: string): string {
  return text
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[^\w\s]/g, '')
    .trim();
}

class ReviewerStore {
  private entries: QuestionEntry[] = [];

  getAll(): QuestionEntry[] {
    return [...this.entries].sort(
      (a, b) => new Date(b.lastSeenAt).getTime() - new Date(a.lastSeenAt).getTime()
    );
  }

  getByQuestion(question: string): QuestionEntry | undefined {
    const normalized = normalizeQuestion(question);
    return this.entries.find(
      (e) => normalizeQuestion(e.question) === normalized
    );
  }

  upsert(entry: Omit<QuestionEntry, 'seenCount' | 'lastSeenAt' | 'createdAt'>): QuestionEntry {
    const existing = this.getByQuestion(entry.question);
    const now = new Date().toISOString();

    if (existing) {
      existing.seenCount += 1;
      existing.lastSeenAt = now;
      // Update all fields from latest submission
      existing.choices = entry.choices;
      existing.correctAnswer = entry.correctAnswer;
      if (entry.domain) {
        existing.domain = entry.domain;
      }
      return existing;
    }

    const newEntry: QuestionEntry = {
      ...entry,
      seenCount: 1,
      lastSeenAt: now,
      createdAt: now,
    };
    this.entries.push(newEntry);
    return newEntry;
  }

  remove(id: string): boolean {
    const index = this.entries.findIndex((e) => e.id === id);
    if (index === -1) return false;
    this.entries.splice(index, 1);
    return true;
  }

  getCount(): number {
    return this.entries.length;
  }
}

export const reviewerStore = new ReviewerStore();
