export const runtime = 'nodejs';

import { reviewerStore } from '@/lib/reviewer-store';
import { broadcastToSSE } from '../../stream/route';
import { z } from 'zod';

const entrySchema = z.object({
  question: z.string().min(1),
  choices: z.array(z.object({ label: z.string(), content: z.string() })).min(1),
  correctAnswer: z.array(z.string()).min(1),
  domain: z.string().optional().default(''),
});

export async function GET() {
  const entries = reviewerStore.getAll();
  return Response.json({ entries, count: reviewerStore.getCount() });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const parsed = entrySchema.safeParse(body);

    if (!parsed.success) {
      return Response.json(
        { error: 'Invalid request body', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const { question, choices, correctAnswer, domain } = parsed.data;
    const entry = reviewerStore.upsert({
      id: crypto.randomUUID(),
      question,
      choices,
      correctAnswer,
      domain,
    });

    const timestamp = new Date().toISOString();
    broadcastToSSE(JSON.stringify({ type: 'qa_entry', entry, timestamp }));

    return Response.json({ success: true, entry });
  } catch (error) {
    console.error('Reviewer POST error:', error);
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: Request) {
  try {
    const { id } = await request.json() as { id: string };
    if (!id) {
      return Response.json({ error: 'Missing id' }, { status: 400 });
    }

    const removed = reviewerStore.remove(id);
    return Response.json({ success: removed });
  } catch (error) {
    console.error('Reviewer DELETE error:', error);
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
