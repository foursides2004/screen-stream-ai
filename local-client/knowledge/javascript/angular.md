# Angular Core Concepts

## Angular Architecture

### Component-Based Architecture
- Application built from components
- Each component has template, class, and metadata
- Components form a tree hierarchy
- Root component bootstraps the application

### Angular Module (NgModule)
- Organizes related code into cohesive blocks
- Declares components, directives, pipes
- Imports other modules for shared functionality
- Provides services via dependency injection
- Bootstraps the root component

```typescript
@NgModule({
  declarations: [AppComponent, HeaderComponent],
  imports: [BrowserModule, HttpClientModule],
  providers: [DataService],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

### Standalone Components (Angular 14+)
- No need for NgModule declarations
- Import dependencies directly
- Simplified module system
- Better tree-shaking

```typescript
@Component({
  selector: 'app-user',
  standalone: true,
  imports: [CommonModule, UserCardComponent],
  templateUrl: './user.component.html'
})
export class UserComponent { }
```

## Components

### Component Definition
```typescript
@Component({
  selector: 'app-user',
  template: `<h1>{{ name }}</h1>`,
  styleUrls: ['./user.component.css']
})
export class UserComponent implements OnInit {
  name = 'John';
}
```

### Component Lifecycle
1. **constructor**: Class instantiation
2. **ngOnChanges**: Input properties change
3. **ngOnInit**: Component initialization
4. **ngDoCheck**: Custom change detection
5. **ngAfterContentInit**: Content projected into component
6. **ngAfterContentChecked**: Content checked
7. **ngAfterViewInit**: Component view initialized
8. **ngAfterViewChecked**: Component view checked
9. **ngOnDestroy**: Component destruction

### Data Binding
- **Interpolation**: `{{ expression }}`
- **Property Binding**: `[property]="expression"`
- **Event Binding**: `(event)="handler()"`
- **Two-Way Binding**: `[(ngModel)]="property"`

### Input and Output
```typescript
// Parent to child
@Input() name: string;

// Child to parent
@Output() selected = new EventEmitter<string>();
```

## Directives

### Structural Directives
- `*ngIf`: Conditionally render elements
- `*ngFor`: Iterate over collections
- `*ngSwitch`: Multi-way conditional rendering

```html
<div *ngIf="isVisible">Visible</div>
<li *ngFor="let item of items">{{ item.name }}</li>
<div [ngSwitch]="status">
  <span *ngSwitchCase="'active'">Active</span>
</div>
```

### Attribute Directives
- `ngClass`: Add/remove CSS classes
- `ngStyle`: Add/remove inline styles

```html
<div [ngClass]="{ 'active': isActive, 'disabled': isDisabled }"></div>
<div [ngStyle]="{ 'color': textColor }"></div>
```

### Custom Directives
```typescript
@Directive({ selector: '[appHighlight]' })
export class HighlightDirective {
  @HostListener('mouseenter') onMouseEnter() {
    this.highlight('yellow');
  }
  constructor(private el: ElementRef) {}
  private highlight(color: string) {
    this.el.nativeElement.style.backgroundColor = color;
  }
}
```

## Pipes

### Built-in Pipes
- `date`: Format dates
- `currency`: Format currency values
- `uppercase`/`lowercase`: Case conversion
- `json`: Convert to JSON string
- `async`: Unwrap observables/promises
- `slice`: Extract portion of array/string

```html
{{ date | date:'medium' }}
{{ price | currency:'USD' }}
{{ name | uppercase }}
{{ data | async }}
```

### Custom Pipes
```typescript
@Pipe({ name: 'exponential' })
export class ExponentialPipe implements PipeTransform {
  transform(value: number, exponent: number = 1): number {
    return Math.pow(value, exponent);
  }
}
```

## Services and Dependency Injection

### Service Definition
```typescript
@Injectable({ providedIn: 'root' })
export class UserService {
  private users: User[] = [];
  
  getUsers(): Observable<User[]> {
    return of(this.users);
  }
}
```

### Dependency Injection
```typescript
@Component({ /* ... */ })
export class UserComponent {
  constructor(private userService: UserService) {}
}
```

### Injection Tokens
```typescript
export const API_URL = new InjectionToken<string>('API_URL');

// Provider
providers: [{ provide: API_URL, useValue: 'https://api.example.com' }]

// Usage
constructor(@Inject(API_URL) private apiUrl: string) {}
```

## Reactive Forms

### Form Setup
```typescript
this.form = this.fb.group({
  name: ['', [Validators.required, Validators.minLength(3)]],
  email: ['', [Validators.required, Validators.email]],
  age: [null, [Validators.min(18), Validators.max(120)]]
});
```

### Form Template
```html
<form [formGroup]="form" (ngSubmit)="onSubmit()">
  <input formControlName="name">
  <div *ngIf="form.get('name')?.invalid && form.get('name')?.touched">
    Name is required (min 3 chars)
  </div>
  <button type="submit" [disabled]="form.invalid">Submit</button>
</form>
```

### Form Validation
- **Validators.required**: Field must have value
- **Validators.email**: Must be valid email
- **Validators.minLength(n)**: Minimum length
- **Validators.pattern(regex)**: Match pattern
- **Custom validators**: Function returning ValidationErrors | null

## Template-Driven Forms

### Form Setup
```html
<form #form="ngForm" (ngSubmit)="onSubmit(form)">
  <input name="name" ngModel required minlength="3">
  <input name="email" ngModel required email>
  <button type="submit" [disabled]="form.invalid">Submit</button>
</form>
```

## HTTP Client

### Basic Usage
```typescript
constructor(private http: HttpClient) {}

getUsers(): Observable<User[]> {
  return this.http.get<User[]>('/api/users');
}

createUser(user: User): Observable<User> {
  return this.http.post<User>('/api/users', user);
}
```

### Interceptors
```typescript
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler) {
    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    return next.handle(authReq);
  }
}
```

## Routing

### Route Configuration
```typescript
const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'users', component: UsersComponent },
  { path: 'users/:id', component: UserDetailComponent },
  { path: '**', component: NotFoundComponent }
];
```

### Route Parameters
```typescript
// In component
this.route.params.subscribe(params => {
  this.userId = params['id'];
});

// Or using snapshot
this.userId = this.route.snapshot.params['id'];
```

### Guards
```typescript
@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    return this.authService.isLoggedIn();
  }
}
```

## RxJS and Observables

### Common Operators
- **map**: Transform values
- **filter**: Select values
- **switchMap**: Switch to new observable
- **mergeMap**: Flatten concurrent observables
- **tap**: Side effects
- **catchError**: Handle errors
- **combineLatest**: Combine latest values from multiple observables

```typescript
this.http.get<User[]>('/api/users').pipe(
  map(users => users.filter(u => u.active)),
  tap(users => console.log(users)),
  catchError(this.handleError)
);
```

### Subjects
- **BehaviorSubject**: Requires initial value, emits current value to new subscribers
- **ReplaySubject**: Replays last N values to new subscribers
- **Subject**: No initial value, no replay

```typescript
private userSubject = new BehaviorSubject<User | null>(null);
user$ = this.userSubject.asObservable();
```

## Change Detection

### Default Strategy
- Checks entire component tree on every event
- Can be expensive in large applications

### OnPush Strategy
- Only checks when:
  - Input reference changes
  - Event handler triggered in component
  - Explicitly triggered via `markForCheck()`
- Better performance

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
```

## Angular CLI

### Common Commands
```bash
ng new my-app          # Create new project
ng generate component  # Generate component
ng generate service    # Generate service
ng generate module     # Generate module
ng build               # Build for production
ng serve               # Start dev server
ng test                # Run unit tests
ng e2e                 # Run e2e tests
```

### Configuration
- `angular.json`: Workspace configuration
- `.browserslistrc`: Browser support targets
- `tsconfig.json`: TypeScript configuration
