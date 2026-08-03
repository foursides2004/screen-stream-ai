# SFCC Service Classes

SFCC provides built-in service classes for external system integrations. Each service class handles a specific protocol.

## Available Service Classes

### HTTPService (dw.net.HTTPService)
- Used for making HTTP/HTTPS requests to external REST/SOAP APIs
- Supports GET, POST, PUT, DELETE, PATCH methods
- Configured via Service Framework in Business Manager

### HTTPFormService (dw.net.HTTPFormService)
- Used for HTTP form-based integrations
- Sends data as application/x-www-form-urlencoded
- Commonly used for payment gateway and shipping carrier integrations

### FTPService (dw.net.FTPService)
- Used for standard FTP and SFTP file transfers
- Supports file upload, download, and directory operations
- Commonly used for catalog imports/exports and order exchanges

### SMTPService (dw.net.SMTPService)
- Used for sending emails via SMTP protocol
- Configured with mail server credentials in Business Manager

## Service Framework
- Services are configured in Business Manager under Administration > Operations > Services
- Each service has a service profile with connection credentials
- Services are called via `.ServiceModel.getService(serviceID)`

## Important Notes
- WebService and RestService are NOT actual SFCC service class names
- SOAP integrations are handled via HTTPService, not a separate SOAP class
- All service classes are in the `dw.net` package
