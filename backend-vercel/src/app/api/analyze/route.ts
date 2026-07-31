export const runtime = 'nodejs';

import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';
import { broadcastToSSE } from '../stream/route';

const openrouter = createOpenAI({
  baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY,
});

const MODEL = process.env.OPENROUTER_MODEL || 'google/gemini-2.0-flash-exp:free';
const APP_SECRET = process.env.APP_SECRET_KEY;

const OPENROUTER_HEADERS: Record<string, string> = {
  'HTTP-Referer': process.env.OPENROUTER_REFERER || 'http://localhost:3000',
  'X-Title': process.env.OPENROUTER_TITLE || 'Screen Stream AI Assistant',
};

interface AnalyzeRequest {
  image: string;
  secretKey: string;
  domain?: string;
}

export async function POST(request: Request) {
  try {
    // Get the raw text and log it for debugging
    const text = await request.text();
    console.log('[DEBUG] Raw request text length:', text.length);
    console.log('[DEBUG] Raw request text:', text);

    let body: AnalyzeRequest;
    try {
      body = JSON.parse(text);
    } catch (e) {
      console.error('[DEBUG] JSON parse error:', e);
      return new Response(
        JSON.stringify({ error: 'Invalid JSON body', detail: String(e) }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const { image, secretKey, domain } = body;

    if (!secretKey || secretKey !== APP_SECRET) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized: Invalid secret key' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (!image || !image.startsWith('data:image/')) {
      return new Response(
        JSON.stringify({ error: 'Invalid image format. Expected base64 data URL.' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const domainContext = domain
      ? `\n\nDOMAIN CONTEXT: This is an official ${domain} exam/assessment. Treat all questions as formal ${domain} exam questions and provide accurate answers based on ${domain} documentation, official guidelines, and established best practices.`
      : '';

    const result = await streamText({
      model: openrouter(MODEL) as any,
      messages: [
        {
          role: 'system',
          content: `You are an AI assistant that reads screen captures and solves problems visible on screen.

PRIMARY TASK: Look at the screen capture carefully. If there are questions, quizzes, tests, or assessments visible, READ each question and PROVIDE THE CORRECT ANSWER(S) directly.

IMPORTANT RULES:
- If there is a question on screen, answer it correctly with the right answer
- If there are MULTIPLE questions, answer ALL of them, each clearly labeled
- If there are multiple-choice options, identify the correct option
- Provide the actual answer content, not a description of the test
- NO explanations about what you see, NO descriptions like "taking a test"
- NO markdown, NO introductions, NO conclusions
- Just the answer(s), nothing else
- For multi-select questions, provide ALL correct options${domainContext}

EXAMPLES OF GOOD RESPONSES:
- "C" (for a multiple choice)
- "Paris" (for "What is the capital of France?")
- "B. O(n log n)\nC. O(n)" (for multiple questions)

EXAMPLES OF BAD RESPONSES:
- "Taking an online test"
- "The user is answering a quiz"
- "I see a multiple choice question"`,
        },
        {
          role: 'user',
          content: [
            { type: 'text', text: 'Read the questions on this screen and provide the correct answer(s) for each one. If there are multiple questions, answer all of them.' },
            { type: 'image', image },
          ],
        },
      ],
      maxTokens: 2048,
      temperature: 0.3,
      headers: OPENROUTER_HEADERS,
      onFinish: async (result) => {
        const content = result.text;
        if (content) {
          const message = JSON.stringify({ type: 'analysis', content, isComplete: true, timestamp: new Date().toISOString() });
          broadcastToSSE(message);
        }
      },
    });

    return result.toDataStreamResponse();
  } catch (error) {
    console.error('Analyze error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}