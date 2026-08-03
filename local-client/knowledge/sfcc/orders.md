# SFCC Order and Basket Management

## Basket vs Order

- **Basket** — The shopping cart before checkout (mutable)
- **Order** — Placed order after checkout (immutable, requires Transaction.wrap())

## Order States

1. **Created** — Initial state
2. **New** — Order placed, awaiting processing
3. **Open** — Order being processed
4. **Completed** — Order fulfilled
5. **Cancelled** — Order cancelled
6. **Replaced** — Order replaced by another

## Order Number Format

- Numeric string (e.g., "1234567890")
- Generated automatically by SFCC
- Unique per site

## Key Order Properties

- `orderNo` — Order number
- `status` — Order status
- `creationDate` — When order was placed
- `totalPrice` — Order total
- `billingAddress` — Billing address
- `shippingAddress` — Shipping address
- `paymentInstruments` — Payment methods used
- `shipments` — Shipment details

## OrderMgr Methods

```javascript
// Get order by number
var order = OrderMgr.getOrder(orderNo);

// Query orders
var orders = OrderMgr.queryOrders("status={2}", "creationDate DESC");
while (orders.hasNext()) {
    var order = orders.next();
}
orders.close(); // Always close!

// Create order from basket
var order = OrderMgr.createOrder(basket);
```

## Transaction Handling

All write operations must be wrapped:
```javascript
Transaction.wrap(function() {
    var order = OrderMgr.createOrder(basket);
    order.setCustomerNo(customerNo);
});
```

## Price Adjustments

- Discounts, promotions, and price overrides
- Can be at order, shipment, or line item level
- Stored as PriceAdjustment objects
