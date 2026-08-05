# RPA Core Concepts

## What is RPA

Robotic Process Automation (RPA) is software technology that enables anyone to configure computer software, or a "robot" to emulate and integrate human actions within digital systems to execute a business process.

RPA robots interpret, trigger systems responses, communicate with other systems and perform repetitive actions. Unlike traditional IT solutions, RPA software can configure itself to perform a wide variety of tasks.

## Attended vs Unattended Automation

### Attended Automation
- Runs on a user's workstation, triggered by user action
- Requires human interaction to start/stop
- Useful for front-office tasks requiring user judgment
- Typically invoked via hotkeys, tray icons, or application events
- Cannot run unattended (needs logged-in desktop session)

### Unattended Automation
- Runs on servers or virtual machines without human intervention
- Scheduled or triggered by events (email, queue, API)
- Used for high-volume back-office processes
- Can run 24/7 across multiple bot instances
- Managed centrally via Control Room/orchestrator

### Hybrid Automation
- Combines attended and unattended capabilities
- Attended bot escalates to unattended for long-running tasks
- Human-in-the-loop pattern for approval workflows

## Types of RPA Bots

### Attended Bots
- Desktop-assist robots triggered by user events
- Run on the same machine as the human worker
- Best for tasks needing human judgment at checkpoints

### Unattended Bots
- Back-office robots running on servers/VMs
- Scheduled or event-triggered execution
- High throughput, no human dependency

### Hybrid Robots
- Switch between attended and unattended modes
- Allow escalation from desktop to server execution

## RPA Use Cases

### Data Entry and Migration
- Copy data between systems without APIs
- Migrate legacy data to modern platforms
- Populate forms from spreadsheets or databases

### Invoice Processing
- Extract data from PDFs/emails
- Match purchase orders to invoices
- Route for approval and post to ERP

### Customer Onboarding
- Validate identity documents
- Create accounts across multiple systems
- Send confirmation communications

### Reporting and Reconciliation
- Pull data from multiple sources
- Generate consolidated reports
- Flag discrepancies for review

### HR Operations
- Process employee onboarding/offboarding
- Update systems with personnel changes
- Generate payroll reports

## RPA vs Traditional Automation

### Traditional Automation
- API-based integration between systems
- Requires developer knowledge and IT involvement
- Brittle — breaks when UI changes
- Best for stable, high-volume system integrations

### RPA
- UI-level automation (no API required)
- Business users can build and maintain
- Resilient — adapts to minor UI changes
- Best for processes spanning multiple systems without APIs

## RPA Architecture Patterns

### Front-Office (Desktop)
- Bots run on user workstations
- User-triggered or event-triggered
- Access to local applications and resources

### Back-Office (Server)
- Bots run on centralized servers/VMs
- Orchestrated by Control Room
- Scalable across multiple bot instances

### Hybrid
- Combination of front-office and back-office
- Task routing between desktop and server bots
- Flexible deployment based on process requirements

## Bot Development Lifecycle

### 1. Discovery
- Identify automation candidates
- Assess process complexity and ROI
- Document process steps and decision points

### 2. Design
- Create process flowcharts
- Define exception handling strategies
- Plan credential management

### 3. Development
- Build automation workflows
- Implement error handling and logging
- Unit test individual components

### 4. Testing
- Integration testing with real systems
- User acceptance testing (UAT)
- Performance and load testing

### 5. Deployment
- Stage to production environment
- Schedule or trigger configuration
- Monitor and optimize

### 6. Operations
- Monitor bot performance and health
- Handle exceptions and escalations
- Continuously improve processes

## Process Complexity Assessment

### Simple (Easy to Automate)
- Rule-based, no judgment needed
- Few exceptions
- Stable UI and business rules
- Single system or simple integrations

### Medium (Moderate Complexity)
- Some decision points
- Moderate exception handling
- Multiple system integrations
- Data validation required

### Complex (Challenging)
- Heavy judgment/decision-making
- Many exception scenarios
- Unstable or frequently changing UIs
- Complex business logic and integrations
