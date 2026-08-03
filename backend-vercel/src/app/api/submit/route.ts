export const runtime = 'nodejs';

import { broadcastToSSE } from '../stream/route';
import { z } from 'zod';

const submitSchema = z.object({
  text: z.string().min(1),
  secretKey: z.string(),
});

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const parsed = submitSchema.safeParse(body);

    if (!parsed.success) {
      return Response.json(
        { error: 'Invalid request body', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const { text, secretKey } = parsed.data;

    if (secretKey !== process.env.APP_SECRET_KEY) {
      return Response.json(
        { error: 'Unauthorized: Invalid secret key' },
        { status: 401 }
      );
    }

    // Broadcast to dashboard as a completed analysis
    const message = JSON.stringify({
      type: 'analysis',
      content: text,
      isComplete: true,
      timestamp: new Date().toISOString(),
    });
    broadcastToSSE(message);

    return Response.json({ success: true });
  } catch (error) {
    console.error('Submit error:', error);
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
