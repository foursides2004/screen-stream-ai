import { createOpenAI } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { createDataStreamResponse } from 'ai';
import { broadcastAnalysis } from '../ws/route';

const openrouter = createOpenAI({
  baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY,
});

const MODEL = process.env.OPENROUTER_MODEL || 'google/gemini-3.5-flash-lite';
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
            { type: 'image', image: image },
          ],
        },
      ],
      maxTokens: 2048,
      temperature: 0.3,
      headers: OPENROUTER_HEADERS,
    });

    return createDataStreamResponse({
      execute: async (dataStream) => {
        let fullContent = '';
        for await (const chunk of result.textStream) {
          fullContent += chunk;
          dataStream.writeData({ type: 'text', content: chunk });

          // Broadcast to dashboard SSE clients
          console.log('[ANALYZE] Broadcasting chunk, length:', fullContent.length);
          broadcastAnalysis({
            type: 'analysis',
            content: fullContent,
            timestamp: new Date().toISOString(),
            isComplete: false,
          });
        }
        dataStream.writeData({ type: 'done', content: '' });

        // Broadcast completion
        console.log('[ANALYZE] Broadcasting completion');
        broadcastAnalysis({
          type: 'analysis',
          content: fullContent,
          timestamp: new Date().toISOString(),
          isComplete: true,
        });
      },
      onError: (error) => {
        console.error('Stream error:', error);
        return error instanceof Error ? error.message : 'Unknown error occurred';
      },
    });
  } catch (error) {
    console.error('Analyze error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}