# SFCC Customer Management

## Customer Types

1. **Registered Customer** — Has an account (authenticated)
2. **Guest Customer** — No account, email-only checkout
3. **Anonymous Customer** — Not logged in, tracked by session

## Customer Properties

- `customerNo` — Unique customer number
- `email` — Customer email
- `firstName`, `lastName` — Name fields
- `group` — Customer group membership
- `addresses` — Saved addresses
- `paymentInstruments` — Saved payment methods

## Customer Groups

- Used for segmentation and targeting
- Control access to content, promotions, and pricing
- Examples: VIP, Wholesale, Loyalty Members
- Assigned via Business Manager or programmatically

## CustomerMgr Methods

```javascript
// Get customer by number
var customer = CustomerMgr.getCustomerByCustomerNumber(customerNo);

// Authenticate customer
var customer = CustomerMgr.authenticateCustomer(login, password);
// Returns null if authentication fails

// Get current customer
var customer = Session.getSession().getCustomer();
```

## Authentication Flow

1. Customer submits login credentials
2. `CustomerMgr.authenticateCustomer()` validates
3. If successful, customer object is returned
4. Customer is associated with session
5. Basket can be merged from anonymous to registered

## Customer Segmentation

- Customer groups enable targeted promotions
- Can be used for personalized pricing
- Content slots can target specific groups
- Campaign qualifiers can target by customer group
