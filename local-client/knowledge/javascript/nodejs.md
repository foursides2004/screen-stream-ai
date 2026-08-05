# Node.js Core Concepts

## Node.js Architecture

### Event-Driven, Non-Blocking I/O
- Single-threaded event loop
- Non-blocking I/O operations
- Event-driven architecture with callbacks/promises
- Built on Chrome's V8 JavaScript engine

### Process Architecture
- **Main Thread**: Event loop, JavaScript execution
- **Worker Threads**: CPU-intensive operations (Node.js 10+)
- **libuv**: Cross-platform async I/O library
- **libuv Thread Pool**: File system, DNS, crypto operations

## Modules and Packages

### CommonJS Modules
```javascript
// Export
module.exports = { name, greet };
exports.name = 'John';

// Import
const { name } = require('./module');
const moment = require('moment');
```

### ES Modules
```javascript
// Export
export const name = 'John';
export function greet() { }
export default class MyClass { }

// Import
import MyClass from './module.js';
import { name, greet } from './module.js';
```

### Package.json
```json
{
  "name": "my-app",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "nodemon": "^2.0.0",
    "jest": "^29.0.0"
  }
}
```

## Express.js Framework

### Basic Server
```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello World' });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### Routing
```javascript
// GET request
app.get('/users', (req, res) => {
  res.json(users);
});

// POST request
app.post('/users', (req, res) => {
  const user = req.body;
  users.push(user);
  res.status(201).json(user);
});

// Route parameters
app.get('/users/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user);
});

// Query parameters
app.get('/search', (req, res) => {
  const { q, page } = req.query;
  // Search logic
});
```

### Middleware
```javascript
// Built-in middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// Custom middleware
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong' });
});
```

### Router
```javascript
const router = express.Router();

router.get('/', (req, res) => {
  res.json(users);
});

router.get('/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  res.json(user);
});

app.use('/users', router);
```

## File System Operations

### Synchronous (Blocking)
```javascript
const fs = require('fs');

// Read file
const data = fs.readFileSync('file.txt', 'utf8');

// Write file
fs.writeFileSync('file.txt', 'Hello World');

// Check file exists
if (fs.existsSync('file.txt')) {
  console.log('File exists');
}
```

### Asynchronous (Non-Blocking)
```javascript
const fs = require('fs/promises');

// Read file
const data = await fs.readFile('file.txt', 'utf8');

// Write file
await fs.writeFile('file.txt', 'Hello World');

// List directory
const files = await fs.readdir('.');

// Create directory
await fs.mkdir('new-dir', { recursive: true });
```

### Streams
```javascript
const fs = require('fs');

// Read stream
const readStream = fs.createReadStream('file.txt');
readStream.on('data', (chunk) => {
  console.log(`Received ${chunk.length} bytes`);
});

// Write stream
const writeStream = fs.createWriteStream('output.txt');
writeStream.write('Hello ');
writeStream.write('World');
writeStream.end();

// Pipe
readStream.pipe(writeStream);
```

## HTTP Module

### Creating Server
```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ message: 'Hello World' }));
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### Making Requests
```javascript
const https = require('https');

// GET request
https.get('https://api.example.com/data', (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => console.log(JSON.parse(data)));
});

// POST request
const postData = JSON.stringify({ name: 'John' });
const options = {
  hostname: 'api.example.com',
  path: '/users',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => console.log(data));
});

req.write(postData);
req.end();
```

## Process Management

### Process Object
```javascript
// Current process
console.log(process.pid);
console.log(process.env.NODE_ENV);
console.log(process.argv);

// Environment variables
process.env.NODE_ENV = 'production';
```

### Child Processes
```javascript
const { exec, spawn } = require('child_process');

// Execute command
exec('ls -la', (error, stdout, stderr) => {
  console.log(stdout);
});

// Spawn process
const child = spawn('ls', ['-la']);
child.stdout.on('data', (data) => console.log(data.toString()));
child.stderr.on('data', (data) => console.error(data.toString()));
```

### Worker Threads
```javascript
const { Worker, isMainThread, parentPort } = require('worker_threads');

if (isMainThread) {
  const worker = new Worker(__filename);
  worker.on('message', (msg) => console.log(msg));
  worker.postMessage({ task: 'process' });
} else {
  parentPort.on('message', (msg) => {
    // Process task
    parentPort.postMessage({ result: 'done' });
  });
}
```

## Error Handling

### Try/Catch
```javascript
try {
  riskyOperation();
} catch (error) {
  console.error(error.message);
} finally {
  cleanup();
}
```

### Uncaught Exceptions
```javascript
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
});
```

### Error Classes
```javascript
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
  }
}

throw new AppError('Not Found', 404);
```

## Testing

### Jest Framework
```javascript
// Simple test
describe('Math', () => {
  it('adds numbers', () => {
    expect(1 + 1).toBe(2);
  });
});

// Async test
describe('API', () => {
  it('fetches users', async () => {
    const users = await fetchUsers();
    expect(users).toHaveLength(3);
  });
});

// Mocking
jest.mock('./module');
jest.fn();
```

### Supertest (API Testing)
```javascript
const request = require('supertest');
const app = require('./app');

describe('GET /users', () => {
  it('returns list of users', async () => {
    const res = await request(app).get('/users');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});
```

## Performance

### Event Loop Monitoring
```javascript
const { monitorEventLoopDelay } = require('perf_hooks');

const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();

setInterval(() => {
  console.log(h.mean / 1e6, 'ms');
  h.reset();
}, 1000);
```

### Memory Management
```javascript
// Check memory usage
console.log(process.memoryUsage());

// Force garbage collection (with flag)
// node --expose-gc app.js
global.gc();
console.log(process.memoryUsage());
```

### Clustering
```javascript
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isPrimary) {
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} died`);
  });
} else {
  require('./app');
}
```
