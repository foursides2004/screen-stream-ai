/**
 * Extract structured Q&A data from Gemini's response text.
 * Gemini returns: plain answer text + a JSON code block.
 */

import type { AnswerChoice } from './reviewer-store';

interface StructuredQA {
  question: string;
  choices: AnswerChoice[];
  correctAnswer: string[];
}

export function extractStructuredQA(text: string): StructuredQA | null {
  // Find the last ```json ... ``` code block
  const jsonBlockRegex = /```json\s*\n([\s\S]*?)\n\s*```/g;
  let lastMatch: RegExpExecArray | null = null;
  let match: RegExpExecArray | null;

  while ((match = jsonBlockRegex.exec(text)) !== null) {
    lastMatch = match;
  }

  if (!lastMatch) return null;

  try {
    const parsed = JSON.parse(lastMatch[1] as string) as Record<string, unknown>;

    // Validate required fields
    if (
      typeof parsed['question'] !== 'string' ||
      !parsed['question'] ||
      !Array.isArray(parsed['choices']) ||
      parsed['choices'].length === 0 ||
      !Array.isArray(parsed['correctAnswer']) ||
      parsed['correctAnswer'].length === 0
    ) {
      return null;
    }

    // Validate choices structure
    const choices = parsed['choices'] as Array<Record<string, unknown>>;
    const validChoices: AnswerChoice[] = choices
      .filter(
        (c) =>
          typeof c['label'] === 'string' &&
          typeof c['content'] === 'string'
      )
      .map((c) => ({
        label: c['label'] as string,
        content: c['content'] as string,
      }));

    if (validChoices.length === 0) return null;

    return {
      question: parsed['question'] as string,
      choices: validChoices,
      correctAnswer: parsed['correctAnswer'] as string[],
    };
  } catch {
    return null;
  }
}
