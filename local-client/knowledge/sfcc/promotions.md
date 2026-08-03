# SFCC Promotions and Campaigns

## Campaign Qualifiers

Campaign qualifiers determine when a campaign is applicable. Valid qualifiers:

1. **Coupon Code** — Customer enters a specific coupon code
2. **Source Code** — Customer arrives via a specific source/traffic origin
3. **Order Total** — Order meets minimum/maximum total thresholds
4. **Customer Groups** — Customer belongs to specific customer segments

All four are valid campaign qualifiers in SFCC.

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
