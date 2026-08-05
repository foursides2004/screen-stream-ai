# TypeScript Core Concepts

## Type System

### Basic Types
```typescript
let name: string = 'John';
let age: number = 30;
let isActive: boolean = true;
let items: any[] = [1, 'two', true];
let nothing: null = null;
let undefined: undefined = undefined;
```

### Arrays
```typescript
let numbers: number[] = [1, 2, 3];
let names: Array<string> = ['John', 'Jane'];
```

### Tuples
```typescript
let person: [string, number] = ['John', 30];
let [name, age] = person; // destructuring
```

### Enums
```typescript
enum Status {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE',
  Pending = 'PENDING'
}

let status: Status = Status.Active;
```

### Any, Unknown, Never
- **any**: Disables type checking (avoid)
- **unknown**: Type-safe any (must narrow before use)
- **never**: Never returns (throw error, infinite loop)

```typescript
let data: any = 'hello'; // no type checking
let safe: unknown = 'hello'; // must narrow
function throwError(msg: string): never { throw new Error(msg); }
```

## Interfaces and Types

### Interfaces
```typescript
interface User {
  id: number;
  name: string;
  email?: string; // optional
  readonly createdAt: Date; // read-only
}

interface Printable {
  print(): void;
}

// Extending interfaces
interface Admin extends User {
  role: string;
}
```

### Type Aliases
```typescript
type ID = string | number;
type Status = 'active' | 'inactive' | 'pending';
type User = {
  id: ID;
  name: string;
  status: Status;
};
```

### Interfaces vs Types
- Interfaces: extend with `extends`, declaration merging
- Types: union, intersection, mapped types, conditional types
- Use interfaces for object shapes, types for unions/intersections

## Functions

### Function Types
```typescript
// Function type
type Callback = (data: string) => void;

// Function with types
function add(a: number, b: number): number {
  return a + b;
}

// Arrow function
const multiply = (a: number, b: number): number => a * b;
```

### Optional and Default Parameters
```typescript
function greet(name: string, greeting?: string): string {
  return `${greeting || 'Hello'}, ${name}`;
}

function greetDefault(name: string, greeting: string = 'Hello'): string {
  return `${greeting}, ${name}`;
}
```

### Rest Parameters
```typescript
function sum(...numbers: number[]): number {
  return numbers.reduce((a, b) => a + b, 0);
}
```

### Function Overloads
```typescript
function format(input: string): string;
function format(input: number): string;
function format(input: string | number): string {
  return typeof input === 'string' ? input : input.toString();
}
```

## Generics

### Generic Functions
```typescript
function identity<T>(arg: T): T {
  return arg;
}

const result = identity<string>('hello'); // 'hello'
const num = identity(42); // 42 (inferred)
```

### Generic Interfaces
```typescript
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

const response: ApiResponse<User> = {
  data: { id: 1, name: 'John' },
  status: 200,
  message: 'OK'
};
```

### Generic Classes
```typescript
class Stack<T> {
  private items: T[] = [];
  
  push(item: T): void {
    this.items.push(item);
  }
  
  pop(): T | undefined {
    return this.items.pop();
  }
}
```

### Generic Constraints
```typescript
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(arg: T): void {
  console.log(arg.length);
}

logLength('hello'); // OK
logLength([1, 2, 3]); // OK
// logLength(123); // Error: number doesn't have length
```

## Utility Types

### Partial and Required
```typescript
type User = { name: string; email: string; age: number };

// All properties optional
type PartialUser = Partial<User>;

// All properties required
type RequiredUser = Required<PartialUser>;
```

### Pick and Omit
```typescript
type UserName = Pick<User, 'name' | 'email'>;
type UserWithoutAge = Omit<User, 'age'>;
```

### Record
```typescript
type UserRoles = Record<string, string[]>;
const roles: UserRoles = {
  admin: ['read', 'write', 'delete'],
  user: ['read']
};
```

### Readonly
```typescript
type ReadonlyUser = Readonly<User>;
const user: ReadonlyUser = { name: 'John', email: 'john@example.com', age: 30 };
// user.name = 'Jane'; // Error: readonly
```

### Exclude and Extract
```typescript
type Status = 'active' | 'inactive' | 'pending';
type ActiveStatus = Extract<Status, 'active' | 'inactive'>;
type InactiveStatus = Exclude<Status, 'active'>;
```

## Type Narrowing

### typeof Guards
```typescript
function process(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  return value.toFixed(2);
}
```

### instanceof Guards
```typescript
function processError(error: Error | string) {
  if (error instanceof Error) {
    return error.message;
  }
  return error;
}
```

### Discriminated Unions
```typescript
type Shape = 
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle': return Math.PI * shape.radius ** 2;
    case 'rectangle': return shape.width * shape.height;
  }
}
```

### Type Guards with in
```typescript
interface Bird { fly(): void; }
interface Fish { swim(): void; }

function move(animal: Bird | Fish) {
  if ('fly' in animal) {
    animal.fly();
  } else {
    animal.swim();
  }
}
```

## Advanced Types

### Intersection Types
```typescript
type HasName = { name: string };
type HasAge = { age: number };
type Person = HasName & HasAge; // { name: string; age: number }
```

### Union Types
```typescript
type StringOrNumber = string | number;
type Status = 'active' | 'inactive' | 'pending';
```

### Conditional Types
```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>; // true
type B = IsString<number>; // false
```

### Mapped Types
```typescript
type Optional<T> = {
  [K in keyof T]?: T[K];
};

type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};
```

## Decorators

### Class Decorators
```typescript
function Sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@Sealed
class Greeter { }
```

### Method Decorators
```typescript
function Log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${key} with`, args);
    return original.apply(this, args);
  };
}

class Calculator {
  @Log
  add(a: number, b: number) { return a + b; }
}
```

### Property Decorators
```typescript
function Validate(target: any, key: string) {
  let value: string;
  const getter = () => value;
  const setter = (newVal: string) => {
    if (newVal.length < 3) {
      throw new Error(`${key} must be at least 3 characters`);
    }
    value = newVal;
  };
  Object.defineProperty(target, key, { get: getter, set: setter });
}

class User {
  @Validate
  name: string;
}
```

## TypeScript Configuration

### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

### Strict Mode Options
- `strictNullChecks`: null/undefined are distinct types
- `strictFunctionTypes`: Function parameter type checking
- `strictBindCallApply`: Binding/calling apply type checking
- `noImplicitAny`: Error on implicit any
- `noImplicitThis`: Error on implicit any this
- `alwaysStrict`: Emit "use strict" in all modules
