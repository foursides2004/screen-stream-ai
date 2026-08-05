# Blue Prism Process Studio and Object Studio

## Process Studio

### What is Process Studio
- Visual development environment for Blue Prism processes
- Drag-and-drop workflow designer
- Each process is a sequence of stages connected by links
- Processes automate end-to-end business workflows
- Saved as XML files within Blue Prism database

### Process Studio Components
- **Main Page**: Entry point of the process (required)
- **Pages**: Sub-processes within the main process
- **Stages**: Individual action steps (decision, action, calculation, etc.)
- **Links**: Connections between stages defining execution flow
- **Data Items**: Variables that store data within the process
- **Collections**: Arrays/lists for storing multiple values

### Process Studio Pages
- Each page is a self-contained sub-process
- Pages can be called from other pages (subroutine pattern)
- Page-in and Page-out for passing data between pages
- Start and End stages mark page boundaries
- Maximum 250 stages per page (recommended best practice)

### Process Execution Flow
1. Process starts at the Start stage
2. Follows links between stages
3. Executes actions, makes decisions, calculates values
4. Handles exceptions with exception stages
5. Ends at the End stage

## Object Studio

### What is Object Studio
- Visual development environment for Blue Prism Business Objects
- Automates interaction with specific applications
- Each Business Object handles one application or system
- Business Objects are reusable across multiple processes
- Separates UI automation logic from business logic

### Object Studio Components
- **Application Modeler**: Defines how to connect to the target application
- **Action Pages**: Business actions the object can perform
- **Element Studio**: Defines UI elements (spies) the object interacts with
- **Data Items**: Variables specific to the object
- **Collections**: Arrays for object-level data storage

### Application Modeler
- Defines connection method to target application
- Connection types:
  - **Windows Application**: Launch or attach to a Windows app
  - **Mainframe Application**: Connect to 3270/5250 terminals
  - **Web Application**: Attach to browser-based applications
  - **Java Application**: Connect via Java Access Bridge
  - **SAP Application**: Direct SAP integration
- Identifies the target application by process name, window title, or path

### Element Spies
- Identify UI elements for automation
- Element attributes used for identification:
  - Window Title, Class, Instance
  - Control Type, Name, ID
  - HTML attributes (for web apps)
  - Text content
- Dynamic elements handled with wildcards or dynamic identification
- Element Studio provides spy, highlight, and verify tools

## Key Blue Prism Stages

### Action Stage
- Calls a Business Object action
- Configures input parameters
- Captures output values
- Links to a specific Business Object and action page

### Decision Stage
- Boolean evaluation (True/False branches)
- Supports complex expressions
- Uses data items and collections in conditions
- No loops — use collection navigation instead

### Choice Stage
- Multi-way branching (like switch/case)
- Evaluates expression and routes to matching branch
- Default branch for unmatched values

### Calculation Stage
- Performs mathematical operations
- Assigns results to data items
- Supports standard operators: +, -, *, /
- Handles date/time calculations

### Data Item Stage
- Defines a variable with a specific data type
- Types: Text, Number, Date/Time, Flag (Boolean), Password
- Can be set as constant or editable
- Initial value configured at design time

### Collection Stage
- Defines an array/list variable
- Stores multiple rows of data
- Used for iterating through lists of items
- Supports Add, Remove, Get, Set Row operations

### Exception Stage
- Throws a business or system exception
- Configurable exception type and message
- Used to signal errors to the calling process
- Caught by exception handling stages

### Block Stage
- Groups multiple stages together
- Used for organizing complex logic
- Does not affect execution flow
- Visual organization only

### Loop Stage
- Iterates over a collection
- Processes each item in sequence
- Provides current item reference
- Used with Get Next Item from Collection

## Business Objects

### What is a Business Object
- Encapsulates automation for a specific application
- Provides reusable actions (Login, Search, Extract, etc.)
- Separates UI automation from business logic
- Managed in Object Studio
- Published for use by processes

### Business Object Actions
- Each action is a page in Object Studio
- Actions have input parameters and output parameters
- Actions are called from Process Studio via Action Stage
- Common action patterns:
  - **Login**: Authenticate to target application
  - **Navigate**: Move between screens/pages
  - **Search**: Find data or records
  - **Extract**: Pull data from the application
  - **Update**: Modify data in the application
  - **Close**: Exit or logout from the application

### VBO (Virtual Business Object)
- Pre-built Business Objects provided by Blue Prism
- Common VBOs:
  - **Utility - Excel**: Read/write Excel files
  - **Utility - File Management**: File operations
  - **Utility - Environment**: System environment access
  - **Work Queues**: Queue management operations
- Custom VBOs created in Object Studio

## Debugging and Testing

### Debugging Tools
- **Step**: Execute one stage at a time
- **Breakpoint**: Pause execution at a specific stage
- **Watch**: Monitor data item values during execution
- **Reset**: Stop and restart process from beginning
- **Output**: View execution log and results

### Testing Approach
- Unit test individual pages and actions
- Integration test with real applications
- Regression test after changes
- Performance test under load

### Debug Mode
- Run process in debug mode from Design Studio
- Step through each stage
- Inspect variable values
- Verify element identification
- Test exception handling
