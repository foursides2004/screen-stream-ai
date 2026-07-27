export const runtime = 'edge';

import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

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
    const body = await request.json() as AnalyzeRequest;
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

    const result = streamText({
      model: openrouter(MODEL) as any,
      messages: [
        {
          role: 'system',
          content: `You are an AI that analyzes screen captures. Return ONLY the direct answer to what the user is asking/doing on screen. No explanations, no formatting, no markdown, no introductions. Just the answer.`,
        },
        {
          role: 'user',
          content: [
            { type: 'text', text: 'Analyze this screen capture and provide helpful insights.' },
            { type: 'image', image },
          ],
        },
      ],
      maxTokens: 2048,
      temperature: 0.3,
      headers: OPENROUTER_HEADERS,
    });

    return (await result).toDataStreamResponse();
  } catch (error) {
    console.error('Analyze error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}