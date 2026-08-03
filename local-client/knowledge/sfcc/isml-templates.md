# SFCC ISML Template Tags Reference

## Include Tags

### isinclude (Modern)
Local include (same request context):
```xml
<isinclude template="components/product/productTile" />
```
Remote include (separate HTTP request, independent caching):
```xml
<isinclude url="${URLUtils.url('Pipeline-Name')}" />
```

### isremote (Legacy)
Same as `<isinclude url="...">` — deprecated, use isinclude instead.

### iscomponent (Legacy)
Same as `<isinclude template="...">` — deprecated, use isinclude instead.

## Caching

### iscache
```xml
<iscache status="on" hours="24" />
<iscache status="off" />
<iscache status="ondemand" />
<iscache type="relative" minute="90" />
<iscache type="relative" second="540" />
<iscache type="daily" hour="2" />
```
- `type="relative"` with `minute` or `second` for relative caching
- `type="daily"` for daily cache refresh at specific hour

## Output

### isprint
```xml
<isprint value="${variable}" />
```
- Outputs a value (auto-escaped)

### ${expression}
```xml
${variable}
${object.method()}
```
- Direct output expression

## Conditionals

### isif / iselse / iselseif
```xml
<isif condition="${variable}">
    Content if true
<iselse />
    Content if false
</isif>

<isif condition="${a}">
    A
<iselseif condition="${b}" />
    B
<iselse />
    C
</isif>
```

## Loops

### isloop
```xml
<isloop items="${collection}" var="item">
    ${item.name}
</isloop>
```

## Variable Assignment

### isset
```xml
<isset variable="varName" value="${expression}" />
```

## Content Type

### iscontent
```xml
<iscontent type="text/html" charset="UTF-8" />
```

## Slot Configuration

### isslot
```xml
<isslot id="slotID" context="category" description="Description" context-object="${pdict.Category}" />
```

## Key Differences: Local vs Remote Include

| Aspect | Local (`template`) | Remote (`url`) |
|---|---|---|
| Request context | Same request | Separate HTTP request |
| Pipeline dictionary | Shared | Independent |
| Caching | Inherited | Independent |
| Performance | Faster | Slower (extra HTTP call) |
| Max depth | N/A | 16 levels |
