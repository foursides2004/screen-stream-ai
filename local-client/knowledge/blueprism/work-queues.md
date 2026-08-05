# Blue Prism Work Queues

## What are Work Queues

Work Queues in Blue Prism are a mechanism for distributing and managing work items across runtime resources. They enable parallel processing, load balancing, and reliable execution of tasks.

## Work Queue Concepts

### Queue Structure
- **Queue**: Container for work items with a defined structure
- **Queue Item**: Individual unit of work within a queue
- **Queue Definition**: Schema defining fields and types for queue items
- **Queue Management**: Adding, removing, and monitoring items

### Queue Item Properties
- **Status**: Pending, Locked, Completed, Deferred, Exception, Pending Completion
- **Priority**: Numeric value (0 = highest, 99999 = lowest)
- **Locked By**: Runtime Resource that has claimed the item
- **Locked Date Time**: When the item was locked
- **Completed Date Time**: When processing finished
- **Retry Count**: Number of times item has been retried
- **Tags**: Custom labels for filtering and reporting

### Queue Item Status Flow
1. **Pending** → Item added to queue, waiting for processing
2. **Locked** → Runtime Resource has claimed the item for processing
3. **Completed** → Processing finished successfully
4. **Exception** → Processing failed with an error
5. **Deferred** → Item temporarily removed from processing (scheduled for later)
6. **Pending Completion** → Item marked complete but awaiting confirmation

## Queue Configuration

### Queue Definition Fields
- Define fields with names and data types
- Supported types: Text, Number, Date, Flag, Password, Collection
- Fields can be marked as required or optional
- Default values can be set for fields

### Queue Configuration Options
- **Maximum Retry Count**: How many times to retry failed items
- **Retry Delay**: Time between retry attempts
- **Work Types**: Categories for queue items
- **Tags**: Labels for filtering and reporting
- **Access Control**: Who can add/remove/manage items

## Queue Operations

### Adding Items to Queue
- **Add to Queue**: Single item addition
- **Bulk Add**: Add multiple items at once
- **CSV Import**: Import items from CSV files
- **API**: Add items via Blue Prism API

### Processing Queue Items
- **Get Next Item**: Retrieve highest priority pending item
- **Lock Item**: Claim an item for processing
- **Complete Item**: Mark item as successfully processed
- **Flag Item**: Mark item as failed with exception details
- **Unlock Item**: Release item back to queue
- **Defer Item**: Temporarily remove from processing

### Queue Monitoring
- **Queue Dashboard**: Real-time view of queue status
- **Item History**: Track processing history for each item
- **Performance Metrics**: Throughput, cycle time, error rate
- **Alerting**: Notifications on queue depth, failures, delays

## Work Queue Best Practices

### Design Principles
- Use queues for work distribution across multiple bots
- Design queue item structure to be self-contained
- Include all necessary data in the queue item
- Minimize dependencies on external resources

### Error Handling
- Implement proper exception handling in queue consumers
- Use retry logic with appropriate delays
- Log detailed error information for debugging
- Set maximum retry count based on error type

### Performance Optimization
- Use appropriate priority levels for time-sensitive items
- Balance queue depth across multiple runtime resources
- Monitor queue processing rates
- Optimize item processing time

### Monitoring and Maintenance
- Regular review of queue metrics
- Cleanup of old completed items
- Monitor for stuck or deadlocked items
- Archive historical queue data

## Queue Integration Patterns

### Producer-Consumer Pattern
- Producer adds items to queue
- Consumer(s) process items from queue
- Decouples production and consumption
- Enables parallel processing

### Fan-Out Pattern
- Single queue feeds multiple runtime resources
- Load balancing across available resources
- Automatic failover on resource failure
- Scalable throughput

### Pipeline Pattern
- Multiple queues in sequence
- Each queue handles a stage of processing
- Items move through pipeline stages
- Enables complex multi-step workflows

### Request-Reply Pattern
- Request item added to input queue
- Worker processes request
- Reply item added to output queue
- Enables asynchronous request-response

## Queue Security

### Access Control
- Role-based permissions for queue operations
- Separate permissions for add, remove, manage
- Audit logging of all queue operations
- Encrypted queue data for sensitive items

### Credential Management
- Queue items can contain credential references
- Credentials stored in Blue Prism credential manager
- Runtime Resources access credentials by name
- Automatic credential rotation support
