export const runtime = 'nodejs';

const sseClients = new Set<ReadableStreamDefaultController>();

function addSSEClient(controller: ReadableStreamDefaultController) {
  sseClients.add(controller);
  console.log(`[SSE] Client connected (total: ${sseClients.size})`);
}

function removeSSEClient(controller: ReadableStreamDefaultController) {
  sseClients.delete(controller);
  console.log(`[SSE] Client disconnected (total: ${sseClients.size})`);
}

export function broadcastToSSE(data: string) {
  const message = `data: ${data}\n\n`;
  const encoder = new TextEncoder();
  const encoded = encoder.encode(message);

  for (const client of sseClients) {
    try {
      client.enqueue(encoded);
    } catch (e) {
      console.error('[SSE] Broadcast error:', e);
      sseClients.delete(client);
    }
  }
}

export async function GET() {
  const encoder = new TextEncoder();
  let controllerRef: ReadableStreamDefaultController | null = null;

  const stream = new ReadableStream({
    start(controller) {
      controllerRef = controller;
      addSSEClient(controller);
    },
    cancel() {
      if (controllerRef) {
        removeSSEClient(controllerRef);
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}

export const dynamic = 'force-dynamic';