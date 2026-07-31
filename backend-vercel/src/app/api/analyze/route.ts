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

    const { image, secretKey } = body;

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

    const result = await streamText({
      model: openrouter(MODEL) as any,
      messages: [
        {
          role: 'system',
          content: `You are an AI that analyzes screen captures. Return ONLY the direct answer(s) to what the user is asking/doing on screen.

IMPORTANT RULES:
- If there is ONE correct answer, return just that answer
- If there are MULTIPLE correct answers, return ALL of them, each on a new line
- NO explanations, NO formatting, NO markdown, NO introductions, NO conclusions
- Just the answer(s), nothing else`,
        },
        {
          role: 'user',
          content: [
            { type: 'text', text: 'Analyze this screen capture. What is the user asking or doing? Provide all correct answers if multiple apply.' },
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