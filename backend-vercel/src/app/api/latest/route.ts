import { NextResponse } from 'next/server';

type AnalysisData = {
  type: 'analysis' | 'connected' | 'ping' | 'error';
  content: string;
  timestamp: string;
  isComplete?: boolean;
};

let latestAnalysis: AnalysisData | null = null;

export async function POST(request: Request) {
  try {
    const body = await request.json() as AnalysisData;
    latestAnalysis = body;
    console.log('[LATEST] Saved analysis:', body.type, body.isComplete ? 'COMPLETE' : 'streaming');
    return NextResponse.json({ success: true });
  } catch (e) {
    console.error('[LATEST] Error:', e);
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}

export async function GET() {
  if (!latestAnalysis) {
    return NextResponse.json({ type: 'waiting', content: '' });
  }
  return NextResponse.json(latestAnalysis);
}