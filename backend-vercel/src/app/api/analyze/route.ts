export const runtime = 'edge';

import { streamText } from 'ai';
import OpenAI from 'openai';

const openrouter = new OpenAI({
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
      model: openrouter(MODEL),
      messages: [
        {
          role: 'system',
          content: `You are an AI assistant that analyzes screen captures and provides helpful insights.
You are viewing the user's screen in real-time. Be concise, helpful, and observant.
Focus on actionable insights, code review, UI analysis, debugging help, or general assistance.
Format responses in clean Markdown with code blocks where appropriate.`,
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

    return result.toDataStreamResponse();
  } catch (error) {
    console.error('Analyze error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}