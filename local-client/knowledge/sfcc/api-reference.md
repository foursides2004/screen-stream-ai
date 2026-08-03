# SFCC Scripting API Reference

## OrderMgr (dw.order.OrderMgr)

### queryOrders
```javascript
OrderMgr.queryOrders(selector: String, sorting?: SortString, pagination?: Pagination): SeekableIterator
```
- Returns a **SeekableIterator** of Order objects
- Always call `.close()` on the iterator when done
- Example: `var orders = OrderMgr.queryOrders("status={2}", "creationDate DESC");`

**Valid variable declarations for queryOrders:**
- `var orderList : SeekableIterator = dw.order.OrderMgr.queryOrders(queryAttributes, sortString);` ✓
- `var orderList = dw.order.OrderMgr.queryOrders(queryAttributes, sortString);` ✓
- `var orderList : Collection = dw.order.OrderMgr.queryOrders(...);` ✗ (wrong type)
- `var orderList : Iterator = dw.order.OrderMgr.queryOrders(...);` ✗ (wrong type, it's SeekableIterator not Iterator)

### getOrder
```javascript
OrderMgr.getOrder(orderNo: String): Order
```
- Returns an Order object by order number
- Returns null if not found

### createOrder
```javascript
OrderMgr.createOrder(basket: Basket): Order
```
- Creates an order from a basket

## ProductMgr (dw.catalog.ProductMgr)

### getProduct
```javascript
ProductMgr.getProduct(productID: String): Product
```
- Returns a **Product** object
- Returns null if product not found or not in current site catalog
- Always null-check the result before using

### queryProducts
```javascript
ProductMgr.queryProducts(): ProductSearchHitIterator
```
- Returns an iterator of ProductSearchHit objects

## CustomerMgr (dw.customer.CustomerMgr)

### getCustomerByCustomerNumber
```javascript
CustomerMgr.getCustomerByCustomerNumber(customerNo: String): Customer
```
- Returns a Customer object by customer number

### authenticateCustomer
```javascript
CustomerMgr.authenticateCustomer(login: String, password: String): Customer
```
- Authenticates a customer and returns the Customer object
- Returns null if authentication fails

## Session (dw.system.Session)

### getSession
```javascript
Session.getSession(): Session
```
- Returns the current session object

### getSessionID
```javascript
Session.getSessionID(): String
```
- Returns the session ID string

## Site (dw.system.Site)

### getCurrent
```javascript
Site.getCurrent(): Site
```
- Returns the current site object

### getCustomPreferenceValue
```javascript
Site.getCustomPreferenceValue(preferenceID: String): Object
```
- Returns a custom preference value

## Transaction (dw.system.Transaction)

### wrap
```javascript
Transaction.wrap(callback: Function): Object
```
- Wraps a callback in a transaction
- All write operations must be inside Transaction.wrap()

## SeekableIterator Methods
- `.hasNext()` — Returns true if more results
- `.next()` — Returns the next object
- `.seekTo(index)` — Positions iterator at specific index
- `.getPosition()` — Returns current position
- `.close()` — Closes iterator and frees resources (ALWAYS call this)
