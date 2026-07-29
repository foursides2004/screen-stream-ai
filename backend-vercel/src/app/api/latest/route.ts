import { kv } from '@vercel/kv';
import { NextResponse } from 'next/server';

type AnalysisData = {
  type: 'analysis' | 'connected' | 'ping' | 'error';
  content: string;
  timestamp: string;
  isComplete?: boolean;
};

const LATEST_KEY = 'latest_analysis';

export async function POST(request: Request) {
  try {
    const body = await request.json() as AnalysisData;
    await kv.set(LATEST_KEY, body);
    console.log('[LATEST] Saved analysis:', body.type, body.isComplete ? 'COMPLETE' : 'streaming');
    return NextResponse.json({ success: true });
  } catch (e) {
    console.error('[LATEST] Error:', e);
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}

export async function GET() {
  try {
    const data = await kv.get<AnalysisData>(LATEST_KEY);
    if (!data) {
      return NextResponse.json({ type: 'waiting', content: '' });
    }
    return NextResponse.json(data);
  } catch (e) {
    console.error('[LATEST] GET Error:', e);
    return NextResponse.json({ type: 'waiting', content: '' });
  }
}