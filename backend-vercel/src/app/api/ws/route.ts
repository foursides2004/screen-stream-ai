// SSE Broadcast - Pure Edge Runtime compatible
// No Node.js built-ins (fs, path, etc.) - uses in-memory Set

type SSEController = {
  controller: ReadableStreamDefaultController;
  encoder: TextEncoder;
};

type AnalysisData = {
  type: 'analysis' | 'connected' | 'ping' | 'error';
  content: string;
  timestamp: string;
  isComplete?: boolean;
};

// Global in-memory store (Edge runtime compatible)
const g = globalThis as typeof globalThis & {
  __sseClients?: Set<SSEController>;
  __ssePingInterval?: NodeJS.Timeout;
};

if (!g.__sseClients) {
  g.__sseClients = new Set<SSEController>();
  console.log('[SSE] Global store initialized');
}

const sseClients = g.__sseClients!;

export function addSSEClient(controller: ReadableStreamDefaultController) {
  const encoder = new TextEncoder();
  sseClients.add({ controller, encoder });
  console.log(`[SSE] Client connected (total: ${sseClients.size})`);

  try {
    controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'connected', content: 'Connected to stream' })}\n\n`));
  } catch (e) {
    console.error('[SSE] Failed to send initial message:', e);
  }
}

export function removeSSEClient(controller: ReadableStreamDefaultController) {
  for (const client of sseClients) {
    if (client.controller === controller) {
      sseClients.delete(client);
      console.log(`[SSE] Client disconnected (total: ${sseClients.size})`);
      break;
    }
  }
}

export function broadcastAnalysis(data: AnalysisData) {
  const message = JSON.stringify(data);
  const payload = `data: ${message}\n\n`;

  console.log(`[SSE] Broadcasting to ${sseClients.size} clients:`, data.type, data.isComplete ? 'COMPLETE' : 'streaming');

  for (const client of sseClients) {
    try {
      client.controller.enqueue(client.encoder.encode(payload));
    } catch (e) {
      console.error('[SSE] Failed to send to client:', e);
      sseClients.delete(client);
    }
  }
}

// Keep-alive ping
if (!g.__ssePingInterval) {
  g.__ssePingInterval = setInterval(() => {
    const pingPayload = `data: ${JSON.stringify({ type: 'ping', content: '' })}\n\n`;
    for (const client of sseClients) {
      try {
        client.controller.enqueue(client.encoder.encode(pingPayload));
      } catch (e) {
        sseClients.delete(client);
      }
    }
  }, 30000);
}