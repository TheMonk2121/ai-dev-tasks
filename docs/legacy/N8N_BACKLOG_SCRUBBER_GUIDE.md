<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- ARCHIVED: Historical guide. For current n8n scrubber, see `400_n8n-backlog-scrubber-guide.md`. -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_performance-optimization-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_system-overview.md -->

# n8n Backlog Scrubber Workflow Guide

## Overview

The n8n Backlog Scrubber Workflow automatically calculates and updates scoring metadata in the backlog file. This system provides:

- **Automated Scoring**: No manual calculation needed
- **Consistent Updates**: All scores use the same formula
- **Error Prevention**: Validates data before updating
- **Audit Trail**: Logs all changes for review
- **Webhook Integration**: Trigger from n8n workflows
- **Health Monitoring**: Real-time status checks
- **Backup Protection**: Automatic file backups

## Architecture

### Components

1. **BacklogScrubber Class**(`src/n8n_workflows/backlog_scrubber.py`)
  - Core scoring logic and file management
  - Handles parsing, validation, and updates
  - Provides statistics and error handling

2.**Webhook Server**(`src/n8n_workflows/backlog_webhook.py`)
  - Flask-based webhook endpoint
  - RESTful API for n8n integration
  - Health checks and monitoring

3.**Demo Script**(`demo_backlog_scrubber.py`)
  - Comprehensive demonstration of features
  - Testing and validation utilities

4.**Test Suite**(`tests/test_backlog_scrubber.py`)
  - Unit and integration tests
  - Comprehensive coverage of all features

## Scoring Formula

The backlog scrubber uses the following formula to calculate priority scores:

```text
Score = (BV + TC + RR + LE) / Effort
```

Where:
- **BV**(Business Value): 0-10 scale
- **TC**(Technical Complexity): 0-10 scale  
- **RR**(Risk/Reward): 0-10 scale
- **LE**(Learning Experience): 0-10 scale
- **Effort**: Estimated effort in story points

## Usage

### Standalone Usage

```bash
# Run the backlog scrubber directly
python3 src/n8n_workflows/backlog_scrubber.py

# With custom backlog path
python3 src/n8n_workflows/backlog_scrubber.py --backlog-path /path/to/backlog.md

# Dry run (show changes without writing)
python3 src/n8n_workflows/backlog_scrubber.py --dry-run

# Verbose output
python3 src/n8n_workflows/backlog_scrubber.py --verbose
```text

### Webhook Server

```bash
# Start the webhook server
python3 src/n8n_workflows/backlog_webhook.py

# With custom configuration
python3 src/n8n_workflows/backlog_webhook.py --host 0.0.0.0 --port 5001 --debug
```text

### Demo Script

```bash
# Run comprehensive demo
python3 demo_backlog_scrubber.py
```markdown

## API Endpoints

### Webhook Endpoint

- *POST**`/webhook/backlog-scrubber`

Request body:
```json
{
  "action": "scrub",
  "dry_run": false,
  "backlog_path": "optional/path/to/backlog.md"
}
```yaml

Response:
```json
{
  "success": true,
  "action": "scrub",
  "dry_run": false,
  "items_processed": 20,
  "scores_updated": 5,
  "errors_found": 0,
  "timestamp": "2024-08-06T03:17:11.590241"
}
```yaml

### Health Check**GET**`/health`

Response:
```json
{
  "status": "healthy",
  "service": "backlog-scrubber-webhook",
  "timestamp": "2024-08-06T03:17:11.590241"
}
```yaml

### Statistics**GET**`/stats`

Response:
```json
{
  "success": true,
  "statistics": {
    "items_processed": 20,
    "scores_updated": 5,
    "errors_found": 0,
    "last_run": "2024-08-06T03:17:11.590241"
  },
  "timestamp": "2024-08-06T03:17:11.590241"
}
```yaml

## n8n Integration

### Workflow Structure

1.**Webhook Trigger**- Path: `backlog-scrubber`
  - Method: `POST`

2.**HTTP Request Node**- URL: `<http://localhost:5001/webhook/backlog-scrubber`>
  - Method: `POST`
  - Body: `{{ $json }}`

3.**Function Node**```javascript
   // Process backlog scrubber response
   const response = $input.all()[0].json;
   
   if (response.success) {
       return {
           success: true,
           items_processed: response.items_processed,
           scores_updated: response.scores_updated,
           message: `Processed ${response.items_processed} items, updated ${response.scores_updated} scores`
       };
   } else {
       return {
           success: false,
           error: response.error,
           message: "Backlog scrub failed"
       };
   }
   ```yaml

### Trigger Options

1.**Manual Trigger**: Run when adding new items
2. **Scheduled**: Run weekly to recalculate scores
3. **Webhook**: Trigger from other workflows
4. **File Change**: Trigger when backlog.md is modified

## Configuration

### Environment Variables

- `BACKLOG_PATH`: Path to backlog.md file (the execution engine)
- `ENVIRONMENT`: Environment (development, staging, production)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Command Line Options

#### Backlog Scrubber
- `--backlog-path`: Path to backlog.md file
- `--dry-run`: Show changes without writing
- `--verbose`: Verbose output

#### Webhook Server
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 5001)
- `--debug`: Enable debug mode
- `--backlog-path`: Path to backlog.md file

## Error Handling

### Validation Errors
- Invalid score components (out of range)
- Missing required fields
- Malformed JSON in metadata

### File Errors
- Backlog file not found
- Permission denied
- Disk space issues

### Network Errors
- Webhook server unavailable
- Timeout issues
- Connection problems

## Monitoring

### Health Checks
- Service status monitoring
- Response time tracking
- Error rate monitoring

### Statistics
- Items processed per run
- Scores updated
- Errors encountered
- Last run timestamp

### Logging
- Structured logging with timestamps
- Error tracking and reporting
- Audit trail for all operations

## Backup and Recovery

### Automatic Backups
- Creates `.backup` file before updates
- Preserves original content
- Timestamped backup files

### Recovery Process
1. Stop the webhook server
2. Restore from backup file
3. Restart the service
4. Verify file integrity

## Security Considerations

### Input Validation
- Validates all score components
- Checks for malicious content
- Sanitizes file paths

### Access Control
- Webhook authentication (if needed)
- IP whitelisting (if needed)
- Rate limiting (if needed)

### Data Protection
- No sensitive data in logs
- Secure file handling
- Backup encryption (if needed)

## Troubleshooting

### Common Issues

1. **JSON Parsing Errors**- Check metadata format in backlog
  - Ensure proper quote escaping
  - Validate JSON structure

2.**File Permission Errors**- Check file permissions
  - Verify directory access
  - Ensure write permissions

3.**Webhook Connection Issues**- Verify server is running
  - Check port configuration
  - Test network connectivity

### Debug Mode

Enable debug mode for detailed logging:
```bash
python3 src/n8n_workflows/backlog_webhook.py --debug
```yaml

### Log Analysis

Check logs for:
- Parsing errors
- Validation failures
- Network issues
- Performance metrics

## Performance

### Optimization
- Efficient regex patterns
- Minimal file I/O
- Cached calculations
- Background processing

### Scalability
- Stateless design
- Horizontal scaling support
- Load balancing ready
- Database integration ready

## Future Enhancements

### Planned Features
- Database integration
- Real-time notifications
- Advanced scoring algorithms
- Machine learning integration
- Multi-file support
- Version control integration

### Integration Points
- Git hooks
- CI/CD pipelines
- Monitoring systems
- Alert systems
- Dashboard integration

## Support

### Documentation
- This guide
- Code comments
- API documentation
- Example workflows

### Testing
- Unit tests
- Integration tests
- Performance tests
- Security tests

### Maintenance
- Regular updates
- Security patches
- Performance monitoring
- Backup verification

- --

## Quick Start

1.**Install Dependencies**```bash
   pip install -r requirements.txt
   ```text

2.**Start Webhook Server**```bash
   python3 src/n8n_workflows/backlog_webhook.py
   ```text

3.**Test Integration**```bash
   curl -X POST <http://localhost:5001/webhook/backlog-scrubber> \
    - H "Content-Type: application/json" \
    - d '{"action": "scrub", "dry_run": true}'
   ```

4.**Configure n8n**- Create webhook trigger
  - Add HTTP request node
  - Add function node for processing
  - Test the workflow

5.**Monitor and Maintain**
  - Check health endpoint regularly
  - Monitor logs for errors
  - Verify backup integrity
  - Update as needed

The n8n Backlog Scrubber Workflow is now ready for production deployment! 
