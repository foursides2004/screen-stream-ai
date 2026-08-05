# JavaScript Core Concepts

## Variables and Data Types

### Variable Declarations
- **var**: Function-scoped, hoisted, can be redeclared
- **let**: Block-scoped, hoisted but not initialized (TDZ), cannot be redeclared
- **const**: Block-scoped, must be initialized, cannot be reassigned (but objects/arrays are mutable)

### Data Types
- **Primitive**: string, number, bigint, boolean, undefined, symbol, null
- **Reference**: object, array, function, date, regexp, map, set

### Type Checking
- `typeof` operator for primitives
- `instanceof` for objects
- `Array.isArray()` for arrays
- `Object.prototype.toString.call()` for precise type

## Functions

### Function Declarations
- Hoisted (can be called before declaration)
- Named function with own scope
- `function greet(name) { return `Hello ${name}`; }`

### Function Expressions
- Not hoisted
- Assigned to a variable
- `const greet = function(name) { return `Hello ${name}`; }`

### Arrow Functions
- Concise syntax
- Lexical `this` binding (inherits from enclosing scope)
- No `arguments` object
- Cannot be used as constructors
- `const greet = (name) => `Hello ${name}`;`

### Default Parameters
- `function greet(name = 'World') { return `Hello ${name}`; }`

### Rest Parameters
- `function sum(...numbers) { return numbers.reduce((a, b) => a + b, 0); }`

### Spread Operator
- Array: `[...arr1, ...arr2]`
- Object: `{...obj1, ...obj2}`
- Function: `func(...args)`

## Objects

### Object Literals
```javascript
const person = {
  name: 'John',
  age: 30,
  greet() { return `Hi, I'm ${this.name}`; }
};
```

### Computed Property Names
```javascript
const prop = 'name';
const obj = { [prop]: 'John' };
```

### Destructuring
```javascript
const { name, age } = person;
const [first, second] = array;
const { name: userName } = person; // rename
const { name = 'Default' } = person; // default
```

### Optional Chaining
```javascript
const street = user?.address?.street;
const result = arr?.[0]?.name;
const value = obj?.method?.();
```

### Nullish Coalescing
```javascript
const value = null ?? 'default'; // 'default'
const value = 0 ?? 'default'; // 0
```

## Arrays

### Array Methods
- **map**: Transform each element
- **filter**: Select elements matching condition
- **reduce**: Accumulate into single value
- **find**: First element matching condition
- **some/every**: Test elements against condition
- **flat/flatMap**: Flatten nested arrays
- **sort**: Sort elements (mutates array)
- **slice**: Extract portion (non-mutating)
- **splice**: Add/remove elements (mutating)

### Array Iteration
```javascript
// for...of (values)
for (const item of array) { }

// entries (index + value)
for (const [index, value] of array.entries()) { }

// forEach
array.forEach((item, index) => { });
```

## Promises and Async/Await

### Promises
```javascript
const promise = new Promise((resolve, reject) => {
  if (success) resolve(data);
  else reject(error);
});

promise
  .then(data => console.log(data))
  .catch(error => console.error(error))
  .finally(() => console.log('done'));
```

### Async/Await
```javascript
async function fetchData() {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
}
```

### Promise.all / Promise.allSettled
```javascript
// All must resolve
const [users, posts] = await Promise.all([fetchUsers(), fetchPosts()]);

// Wait for all regardless of outcome
const results = await Promise.allSettled([promise1, promise2]);
```

## Closures and Scope

### Closures
- Function that remembers its lexical scope
- Inner function has access to outer function's variables
- Used for data privacy, factory functions, partial application

```javascript
function counter() {
  let count = 0;
  return {
    increment: () => ++count,
    getCount: () => count
  };
}
```

### Scope Chain
- Global scope → Function scope → Block scope
- Variable lookup goes up the scope chain
- `var` is function-scoped, `let`/`const` are block-scoped

## Prototypes and Classes

### Prototype Chain
- Every object has a `__proto__` property
- Methods looked up via prototype chain
- `Object.getPrototypeOf(obj)` to access prototype

### ES6 Classes
```javascript
class Animal {
  constructor(name) {
    this.name = name;
  }
  speak() {
    return `${this.name} makes a sound`;
  }
}

class Dog extends Animal {
  speak() {
    return `${this.name} barks`;
  }
}
```

### Static Methods
```javascript
class MathUtils {
  static add(a, b) { return a + b; }
}
MathUtils.add(1, 2); // 3
```

## Modules

### ES Modules
```javascript
// Export
export const name = 'John';
export function greet() { }
export default class MyClass { }

// Import
import MyClass from './module.js';
import { name, greet } from './module.js';
import * as Utils from './utils.js';
```

### CommonJS (Node.js)
```javascript
// Export
module.exports = { name, greet };
exports.name = 'John';

// Import
const { name } = require('./module');
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

### Custom Errors
```javascript
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}
```

## Iterators and Generators

### Iterators
```javascript
const iterator = {
  [Symbol.iterator]() {
    let i = 0;
    return {
      next: () => ({
        value: i++,
        done: i > 5
      })
    };
  }
};
```

### Generators
```javascript
function* numberGenerator() {
  yield 1;
  yield 2;
  yield 3;
}

const gen = numberGenerator();
gen.next(); // { value: 1, done: false }
```

## Map and Set

### Map
```javascript
const map = new Map();
map.set('key', 'value');
map.get('key');
map.has('key');
map.delete('key');
map.size;
```

### Set
```javascript
const set = new Set([1, 2, 3, 2]);
set.add(4);
set.has(1);
set.delete(2);
set.size; // 3 (unique values)
```

## WeakMap and WeakSet
- Hold weak references to objects
- Allow garbage collection when no other references exist
- Cannot iterate over entries
- Used for private data, caching, metadata
