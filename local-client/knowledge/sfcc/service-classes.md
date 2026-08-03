# SFCC Service Classes (dw.net package)

## HTTPService

```javascript
var svc = ServiceModel.getService("serviceName");
var result = svc.call(args);
```
- Protocol: HTTP/HTTPS
- Supports: GET, POST, PUT, DELETE, PATCH
- Used for REST and SOAP API integrations
- Configured via Service Framework in Business Manager

## HTTPFormService

```javascript
var svc = ServiceModel.getService("serviceName");
var result = svc.call(args);
```
- Protocol: HTTP/HTTPS
- Content-Type: application/x-www-form-urlencoded
- Used for form-based payment and shipping integrations

## FTPService

```javascript
var svc = ServiceModel.getService("serviceName");
var result = svc.call(args);
```
- Protocol: FTP/SFTP
- Operations: file upload, download, directory listing
- Used for catalog imports/exports and order file exchanges

## SMTPService

```javascript
var svc = ServiceModel.getService("serviceName");
var result = svc.call(args);
```
- Protocol: SMTP
- Used for transactional email delivery

## Service Framework
- Services are configured in Business Manager: Administration > Operations > Services
- Each service has a service profile with connection credentials
- Service IDs are strings passed to `ServiceModel.getService()`
