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