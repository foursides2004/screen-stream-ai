# SFCC Promotions and Campaigns

## Campaign Qualifiers

Campaign qualifiers determine which customers a campaign applies to. There are four qualifier types:

1. **Schedule** — Start and end time/date (determines when campaign is active)
2. **Coupons** — System-generated or merchant-defined codes shoppers enter for discounts
3. **Customer Groups** — Target specific shoppers (System: Everyone/Registered/Unregistered, Static: manually added, Dynamic: rule-based)
4. **Source Codes** — Codes attached to site URL identifying traffic origin, stored in browser cookie

A promotion can have up to 3 qualifier conditions (customer group, coupon, source code). The `qualifierMatchMode` determines whether **all** or **any** conditions must be satisfied.

## Campaign Structure

- **Campaign** → contains Promotions
- **Promotion** → contains Qualifiers (when to apply) and Effects (what discount to give)
- Qualifiers are AND-connected within a campaign
- Campaigns have start/end dates for time-bound activation

## Promotion Types

1. **Product Promotion** — Discount on specific products
2. **Order Promotion** — Discount on entire order
3. **Shipping Promotion** — Free or discounted shipping

## Promotion Effects

- Percentage discount (e.g., 10% off)
- Fixed amount discount (e.g., $5 off)
- Free shipping
- Bonus products (buy X get Y free)

## Source Code Groups

- Source codes track traffic origin
- Linked to campaigns via Source Code Groups
- Used for marketing attribution

## Coupon Code Behavior

- Entered by customer at checkout
- Validated against campaign qualifiers
- One-time use or multi-use coupons
- Can have start/end dates and usage limits
