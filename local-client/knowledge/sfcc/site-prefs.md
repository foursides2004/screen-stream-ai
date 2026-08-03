# SFCC Site Preferences and Custom Attributes

## Custom Attributes

Custom attributes extend standard objects with additional fields:
- Product custom attributes
- Order custom attributes
- Customer custom attributes
- Site preferences

## Externally Managed Attributes

Custom attributes marked "externally-managed":
- **Cannot be edited** by Business Manager users directly
- Values are managed by external systems (PIM, ERP)
- Only administrators with special permissions can modify

## Site Preferences

- Site-wide configuration values
- Defined in Business Manager
- Accessed via `Site.getCustomPreferenceValue()`
- Example: `Site.getCustomPreferenceValue("defaultCurrency")`

## Custom Attribute Types

1. **String** — Text values
2. **Integer** — Whole numbers
3. **Number** — Decimal numbers
4. **Boolean** — True/false
5. **Date** — Date values
6. **EnumOf** — Enumeration (list of allowed values)
7. **SetOf** — Multiple values
8. **CustomObject** — Complex objects

## Property File Localization

- Default locale: `resources/{name}.properties`
- Other locales: `resources/{locale}/{name}.properties`
- Example: `resources/en_GB/account.properties` for en_GB locale

## Caching Custom Attributes

- Custom attribute values can be cached
- Use `<iscache>` tag for template-level caching
- Cache invalidation on attribute update
