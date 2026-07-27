#!/usr/bin/env node
/**
 * Test Runner - Local Batch Validation Suite
 * Scans C:/done for up to 50 images, sends to local API, tracks progress.
 * Path-normalized for Windows using path.normalize and path.join.
 */

const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage } = require('canvas');

const CONFIG = {
  sourceDir: path.normalize('C:/done'),
  apiUrl: 'http://localhost:3000/api/analyze',
  secretKey: process.env.APP_SECRET_KEY || 'your_super_secret_key_here_min_32_chars',
  maxImages: 50,
  maxWidth: 1920,
  supportedExts: ['.png', '.jpg', '.jpeg', '.webp'],
  progressFile: 'test-progress.json',
  requestTimeout: 60000,
  delayBetweenRequests: 1000,
};

const state = {
  totalDiscovered: 0,
  successful: 0,
  failed: 0,
  errors: [],
  remaining: [],
  startTime: Date.now(),
};

function logProgress(message) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${message}`);
}

function loadProgress() {
  if (fs.existsSync(CONFIG.progressFile)) {
    try {
      const data = JSON.parse(fs.readFileSync(CONFIG.progressFile, 'utf-8'));
      state.remaining = data.remaining || [];
      state.successful = data.successful || 0;
      state.failed = data.failed || 0;
      state.errors = data.errors || [];
      logProgress(`[RESUME] Loaded: ${state.remaining.length} remaining, ${state.successful} done, ${state.failed} failed`);
      return true;
    } catch (e) {
      logProgress(`[WARN] Failed to load progress: ${e.message}`);
    }
  }
  return false;
}

function saveProgress() {
  const data = {
    totalDiscovered: state.totalDiscovered,
    successful: state.successful,
    failed: state.failed,
    errors: state.errors,
    remaining: state.remaining,
    lastUpdated: new Date().toISOString(),
  };
  fs.writeFileSync(CONFIG.progressFile, JSON.stringify(data, null, 2));
}

function discoverImages() {
  if (!fs.existsSync(CONFIG.sourceDir)) {
    logProgress(`[ERROR] Source directory not found: ${CONFIG.sourceDir}`);
    process.exit(1);
  }

  const files = fs.readdirSync(CONFIG.sourceDir)
    .filter(f => CONFIG.supportedExts.includes(path.extname(f).toLowerCase()))
    .map(f => path.join(CONFIG.sourceDir, f))
    .sort();

  state.totalDiscovered = files.length;
  logProgress(`[INFO] Discovered ${files.length} image(s) in ${CONFIG.sourceDir}`);

  if (files.length > CONFIG.maxImages) {
    logProgress(`[INFO] Limiting to first ${CONFIG.maxImages} images`);
    return files.slice(0, CONFIG.maxImages);
  }
  return files;
}

async function downscaleImage(imagePath) {
  const img = await loadImage(imagePath);
  const canvas = createCanvas(img.width, img.height);
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);

  if (img.width > CONFIG.maxWidth) {
    const ratio = CONFIG.maxWidth / img.width;
    const newHeight = Math.round(img.height * ratio);
    const scaledCanvas = createCanvas(CONFIG.maxWidth, newHeight);
    const scaledCtx = scaledCanvas.getContext('2d');
    scaledCtx.drawImage(canvas, 0, 0, CONFIG.maxWidth, newHeight);
    logProgress(`[INFO] Downscaled ${path.basename(imagePath)} from ${img.width}px to ${CONFIG.maxWidth}px`);
    return scaledCanvas.toDataURL('image/webp', 0.8);
  }

  return canvas.toDataURL('image/webp', 0.8);
}

async function sendToApi(imageDataUrl, index, total) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CONFIG.requestTimeout);

  try {
    const response = await fetch(CONFIG.apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image: imageDataUrl,
        secretKey: CONFIG.secretKey,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.status === 401) {
      throw new Error('Unauthorized: Check APP_SECRET_KEY matches backend');
    }
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullText = '';

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        fullText += decoder.decode(value, { stream: true });
      }
    }

    return { success: true, response: fullText.substring(0, 200) };
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Request timeout');
    }
    throw error;
  }
}

async function processImage(filePath, index, total) {
  const filename = path.basename(filePath);
  const startTime = Date.now();

  try {
    logProgress(`\n[${index}/${total}] Processing: ${filename}`);

    const imageDataUrl = await downscaleImage(filePath);
    const result = await sendToApi(imageDataUrl, index, total);

    const latency = Date.now() - startTime;
    state.successful++;
    logProgress(`[SUCCESS] ${filename} - ${latency}ms`);
    logProgress(`  Preview: ${result.response}...`);

  } catch (error) {
    state.failed++;
    state.errors.push({
      file: filename,
      error: error.message,
      timestamp: new Date().toISOString(),
    });
    logProgress(`[FAILED] ${filename}: ${error.message}`);
  }
}

async function main() {
  console.log('='.repeat(60));
  console.log('Screen Stream AI - Local Batch Test Runner');
  console.log('='.repeat(60));
  console.log(`Source: ${CONFIG.sourceDir}`);
  console.log(`API: ${CONFIG.apiUrl}`);
  console.log(`Max Images: ${CONFIG.maxImages}`);
  console.log(`Max Width: ${CONFIG.maxWidth}px`);
  console.log('='.repeat(60));

  const resumed = loadProgress();

  let files;
  if (resumed && state.remaining.length > 0) {
    files = state.remaining;
    logProgress(`[RESUME] Continuing with ${files.length} remaining images`);
  } else {
    files = discoverImages();
    state.remaining = [...files];
  }

  if (files.length === 0) {
    logProgress('[INFO] No images to process');
    return;
  }

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    state.remaining = files.slice(i + 1);

    await processImage(file, i + 1, files.length);
    saveProgress();

    if (i < files.length - 1) {
      await new Promise(r => setTimeout(r, CONFIG.delayBetweenRequests));
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('TEST RUN COMPLETE');
  console.log('='.repeat(60));
  console.log(`Total Discovered: ${state.totalDiscovered}`);
  console.log(`Successful: ${state.successful}`);
  console.log(`Failed: ${state.failed}`);
  console.log(`Duration: ${((Date.now() - state.startTime) / 1000).toFixed(1)}s`);
  console.log('='.repeat(60));

  if (state.errors.length > 0) {
    console.log('\nErrors:');
    state.errors.forEach(e => console.log(`  - ${e.file}: ${e.error}`));
  }

  if (fs.existsSync(CONFIG.progressFile)) {
    fs.unlinkSync(CONFIG.progressFile);
    logProgress('[INFO] Cleared progress file (all done)');
  }
}

main().catch(err => {
  logProgress(`[FATAL] ${err.message}`);
  process.exit(1);
});