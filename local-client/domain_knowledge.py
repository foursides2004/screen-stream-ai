"""
Domain-specific knowledge base for exam questions.
Injects factual context into the Gemini prompt to improve answer accuracy.
"""

from __future__ import annotations

# Each domain maps to a knowledge block that gets injected into the system prompt.
# Format: key facts, correct answers for common questions, and reference patterns.

DOMAIN_KNOWLEDGE: dict[str, str] = {
    "SFCC": """
SFCC (Salesforce Commerce Cloud / Demandware) REFERENCE:

CAMPAIGN QUALIFIERS (all of these are valid):
- Coupon Code
- Source Code
- Order Total
- Customer Groups
- Campaign Class

CAMPAIGN TIERS: Campaigns have tiers with qualifiers that determine when a campaign is applicable.

SESSION ATTRIBUTES:
- CurrentSession, CurrentRequest, CurrentCustomer, CurrentHttpParameterMap
- CurrentCampaigns, CurrentCampaignFolders
- CurrentBonusDiscountLineItems

PIPELINE CONTROLLERS:
- Use <isinclude> for including pipelines: <isinclude url="${URLUtils.url('Pipeline-Name')}">
- Use <isremote> for remote pipelines: <isremote url="${URLUtils.url('Pipeline-Name')}">
- Use <iscomponent> for component pipelines: <iscomponent pipeline="Pipeline-Name">

PRODUCT SYSTEM:
- Product objects: product.getID(), product.getName(), product.getPrice()
- Product images: product.getImages('large')
- Product categories: product.getPrimaryCategory()

ORDER SYSTEM:
- Order states: Created, New, Open, Completed, Cancelled, Replaced
- Order includes: shipments, payment instruments, price adjustments
- Basket vs Order: Basket is cart, Order is placed

CUSTOMER SYSTEM:
- Customer profiles: firstName, lastName, email, customerNo
- Customer groups used for segmentation and targeting
- Authenticated vs anonymous customers

PROMOTION SYSTEM:
- Promotion types: Product, Order, Shipping
- Promotion discounts: percentage, fixed amount, free shipping
- Promotion criteria: product, category, customer, coupon, source code

PRICE SYSTEM:
- Price books and price lists
- Promotion prices vs list prices
- Currency handling with Money objects

TEMPLATE SYSTEM (ISML):
- ${variable} for output expressions
- <isif>, <iselse>, <isloop> tags
- <isprint> for variable output
- ${RemoteIncludeVoid()} for remote includes

CUSTOM SCRIPTS:
- BCScript files (.js) in scripts/ directory
- dw.system package for system classes
- dw.order package for order management
- dw.catalog package for catalog management
- dw.util package for utility classes
- dw.io package for I/O operations

API CLASSES:
- ProductMgr: ProductMgr.getProduct(productID)
- OrderMgr: OrderMgr.getOrder(orderNo)
- CustomerMgr: CustomerMgr.getCustomerByCustomerNumber(customerNo)
- Site: Site.getCurrent(), Site.getCustomPreferenceValue()
- Session: Session.getSession(), Session.getSessionID()

COMMON SFCC EXAM ANSWERS:
- Campaign qualifiers: ALL of Coupon Code, Source Code, Order Total, Customer Groups
- Remote pipeline include: <isremote url="${URLUtils.url('Pipeline-Name')}">
- Component include: <iscomponent pipeline="Pipeline-Name">
- Product price: product.getPrice()
- Order number format: numeric string
- Customer authentication: CustomerMgr.authenticateCustomer()
""",
    "AWS": """
AWS REFERENCE:

COMPUTE:
- EC2: virtual servers (instances)
- Lambda: serverless functions
- ECS/EKS: container orchestration
- Elastic Beanstalk: PaaS deployment

STORAGE:
- S3: object storage
- EBS: block storage for EC2
- EFS: managed NFS file system
- Glacier: archival storage

DATABASE:
- RDS: managed relational database (MySQL, PostgreSQL, etc.)
- DynamoDB: managed NoSQL database
- ElastiCache: managed Redis/Memcached
- Redshift: data warehouse

NETWORKING:
- VPC: virtual private cloud
- CloudFront: CDN
- Route 53: DNS service
- ALB/NLB: load balancers

SECURITY:
- IAM: identity and access management
- KMS: key management service
- WAF: web application firewall
- Shield: DDoS protection

MONITORING:
- CloudWatch: monitoring and observability
- CloudTrail: API audit logging
- X-Ray: distributed tracing

COMMON AWS EXAM PATTERNS:
- "Most cost-effective" → usually Reserved Instances, Spot Instances, or S3 Intelligent-Tiering
- "Least operational overhead" → managed services (RDS over self-hosted, Lambda over EC2)
- "High availability" → multi-AZ, auto-scaling, load balancers
- "Disaster recovery" → cross-region replication, backups, pilot light
""",
    "GENERIC_EXAM": """
EXAM STRATEGY:

MULTIPLE CHOICE:
- Read all options before answering
- Eliminate obviously wrong answers first
- Watch for "ALL of the above" — often correct when multiple options seem valid
- Watch for "None of the above" — rarely correct

MULTI-SELECT:
- Look for "Choose the best option(s)" or checkboxes
- ALL valid options must be selected
- Partial credit usually not given — must get ALL correct
- When in doubt, select more rather than fewer

KEY WORDS:
- "BEST" = pick the most appropriate, not just a correct one
- "MOST" = compare all valid options, pick the top one
- "EXCEPT" / "NOT" = find the one that doesn't belong
- "FIRST" = the initial step in a process
""",
}


def get_domain_context(domain: str) -> str:
    """Get domain-specific knowledge for the prompt.

    Args:
        domain: Domain name (e.g., "SFCC", "AWS", "GENERIC_EXAM")

    Returns:
        Knowledge block string, or empty string if domain not found.
    """
    if not domain:
        return ""

    # Case-insensitive lookup
    domain_upper = domain.upper().strip()

    # Direct match
    if domain_upper in DOMAIN_KNOWLEDGE:
        return DOMAIN_KNOWLEDGE[domain_upper]

    # Partial match (e.g., "SFCC Commerce" matches "SFCC")
    for key, value in DOMAIN_KNOWLEDGE.items():
        if key in domain_upper or domain_upper in key:
            return value

    return ""


def list_domains() -> list[str]:
    """Return list of available domain names."""
    return list(DOMAIN_KNOWLEDGE.keys())
