# API Documentation

The Tender Platform provides a comprehensive REST API for integrating with external systems and building custom applications.

## Base URL

```
https://your-domain.com/api/v1
```

For local development:
```
http://localhost:8000/api/v1
```

## Authentication

Most API endpoints require authentication using JWT (JSON Web Token) bearer tokens.

### Obtain Access Token

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "admin",
    "is_active": true,
    "is_email_verified": true
  }
}
```

### Use Access Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Refresh Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

## Core Resources

### Tenders

#### List Tenders

```http
GET /tenders
```

Query Parameters:
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 20, max: 100) - Items per page
- `keywords` (array[string]) - Search keywords
- `okpd2_codes` (array[string]) - OKPD2 codes filter
- `regions` (array[string]) - Regions filter
- `min_budget` (number) - Minimum budget filter
- `max_budget` (number) - Maximum budget filter
- `platforms` (array[string]) - Platforms filter
- `statuses` (array[string]) - Statuses filter
- `customer_inn` (string) - Customer INN filter
- `sort_by` (string, default: "created_at") - Sort field
- `sort_order` (string, enum: ["asc", "desc"], default: "desc") - Sort order

#### Get Tender

```http
GET /tenders/{tender_id}
```

#### Create Tender

```http
POST /tenders
Content-Type: application/json

{
  "external_id": "string",
  "platform": "string",
  "title": "string",
  "customer_name": "string",
  "customer_inn": "string",
  "description": "string",
  "budget": 0,
  "currency": "string",
  "okpd2_codes": ["string"],
  "region": "string",
  "submission_deadline": "2023-01-01T00:00:00Z",
  "contract_start_date": "2023-01-01",
  "contract_end_date": "2023-12-31",
  "status": "string",
  "url": "string",
  "raw_data": {},
  "law_type": "string",
  "purchase_method": "string"
}
```

#### Update Tender

```http
PUT /tenders/{tender_id}
Content-Type: application/json

{
  "title": "string",
  "customer_name": "string",
  "customer_inn": "string",
  "description": "string",
  "budget": 0,
  "currency": "string",
  "okpd2_codes": ["string"],
  "region": "string",
  "submission_deadline": "2023-01-01T00:00:00Z",
  "contract_start_date": "2023-01-01",
  "contract_end_date": "2023-12-31",
  "status": "string",
  "url": "string",
  "raw_data": {}
}
```

#### Delete Tender

```http
DELETE /tenders/{tender_id}
```

#### Search Tenders

```http
POST /tenders/search
Content-Type: application/json

{
  "keywords": ["string"],
  "okpd2_codes": ["string"],
  "regions": ["string"],
  "min_budget": 0,
  "max_budget": 0,
  "platforms": ["string"],
  "statuses": ["string"],
  "submission_deadline_from": "2023-01-01T00:00:00Z",
  "submission_deadline_to": "2023-12-31T23:59:59Z",
  "customer_inn": "string",
  "sort_by": "created_at",
  "sort_order": "desc",
  "page": 1,
  "page_size": 20
}
```

#### Add to Favorites

```http
POST /tenders/{tender_id}/favorites
```

#### Remove from Favorites

```http
DELETE /tenders/{tender_id}/favorites
```

#### Get Favorites

```http
GET /tenders/favorites
```

Query Parameters:
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

### Monitoring Filters

#### List Monitoring Filters

```http
GET /monitoring
```

#### Create Monitoring Filter

```http
POST /monitoring
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "keywords": ["string"],
  "okpd2_codes": ["string"],
  "regions": ["string"],
  "min_budget": 0,
  "max_budget": 0,
  "platforms": ["string"],
  "law_types": ["string"],
  "purchase_methods": ["string"],
  "customer_inns": ["string"],
  "is_active": true,
  "notification_frequency": "real_time"
}
```

#### Get Monitoring Filter

```http
GET /monitoring/{filter_id}
```

#### Update Monitoring Filter

```http
PUT /monitoring/{filter_id}
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "keywords": ["string"],
  "okpd2_codes": ["string"],
  "regions": ["string"],
  "min_budget": 0,
  "max_budget": 0,
  "platforms": ["string"],
  "law_types": ["string"],
  "purchase_methods": ["string"],
  "customer_inns": ["string"],
  "is_active": true,
  "notification_frequency": "daily"
}
```

#### Delete Monitoring Filter

```http
DELETE /monitoring/{filter_id}
```

#### Toggle Filter

```http
PATCH /monitoring/{filter_id}/toggle
Content-Type: application/json

{
  "active": true
}
```

### Analytics

#### Price Statistics

```http
GET /analytics/price-statistics
```

Query Parameters:
- `okpd2_codes` (array[string])
- `region` (string)
- `min_budget` (number)
- `max_budget` (number)

#### Win Probability

```http
POST /analytics/win-probability
Content-Type: application/json

{
  "tender_id": "string",
  "proposed_price": 0,
  "company_experience": 0,
  "similar_contracts_won": 0
}
```

#### Competitor Chart Data

```http
GET /analytics/competitor/{competitor_id}/chart-data
```

Query Parameters:
- `limit` (integer, default: 20, max: 100)

#### Generate Overall Analytics

```http
POST /analytics/generate-overall
Content-Type: application/json

{
  "period_start": "2023-01-01T00:00:00Z",
  "period_end": "2023-12-31T23:59:59Z",
  "okpd2_codes": ["string"],
  "regions": ["string"],
  "include_competitors": true,
  "include_financial": true,
  "include_performance": true
}
```

#### User Performance

```http
GET /analytics/user-performance
```

#### Reports

```http
GET /analytics/reports
```

#### Create Report

```http
POST /analytics/reports
Content-Type: application/json

{
  "report_type": "string",
  "title": "string",
  "description": "string",
  "filters": {}
}
```

### Documents

#### List Documents

```http
GET /documents
```

Query Parameters:
- `tender_id` (string)
- `document_type` (string)
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

#### Upload Document

```http
POST /documents/upload
Content-Type: multipart/form-data

{
  "file": "binary_file_data",
  "tender_id": "string",
  "title": "string",
  "description": "string",
  "document_type": "string"
}
```

#### Get Document

```http
GET /documents/{document_id}
```

#### Update Document

```http
PUT /documents/{document_id}
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "document_type": "string"
}
```

#### Delete Document

```http
DELETE /documents/{document_id}
```

#### Download Document

```http
GET /documents/{document_id}/download
```

### AI Integration

#### Analyze Tender

```http
POST /ai/analyze-tender
Content-Type: application/json

{
  "tender_id": "string",
  "analysis_type": "compliance_check"
}
```

#### Generate Application

```http
POST /ai/generate-application
Content-Type: application/json

{
  "tender_id": "string",
  "company_profile": {}
}
```

#### Generate Technical Specification

```http
POST /ai/generate-tz
Content-Type: application/json

{
  "tender_id": "string",
  "requirements": {}
}
```

#### AI Thresholds

```http
GET /ai/thresholds
```

```http
PUT /ai/thresholds
Content-Type: application/json

{
  "risk_threshold": 0.7,
  "compliance_threshold": 0.9
}
```

### Users

#### Get Current User

```http
GET /users/me
```

#### Update Profile

```http
PUT /users/me
Content-Type: application/json

{
  "full_name": "string",
  "email": "string",
  "company_name": "string",
  "inn": "string",
  "kpp": "string",
  "phone": "string"
}
```

#### List Users (Admin)

```http
GET /users
```

Query Parameters:
- `role` (string)
- `is_active` (boolean)
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

#### Get User (Admin)

```http
GET /users/{user_id}
```

#### Update User (Admin)

```http
PUT /users/{user_id}
Content-Type: application/json

{
  "full_name": "string",
  "email": "string",
  "role": "string",
  "company_name": "string",
  "inn": "string",
  "kpp": "string",
  "phone": "string",
  "is_active": true
}
```

#### Delete User (Admin)

```http
DELETE /users/{user_id}
```

### Notifications

#### List Notifications

```http
GET /notifications
```

Query Parameters:
- `is_read` (boolean)
- `notification_type` (string)
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

#### Get Notification

```http
GET /notifications/{notification_id}
```

#### Mark as Read

```http
PATCH /notifications/{notification_id}/read
```

#### Mark All as Read

```http
PATCH /notifications/read-all
```

#### Delete Notification

```http
DELETE /notifications/{notification_id}
```

### Templates

#### List Templates

```http
GET /templates
```

Query Parameters:
- `template_type` (string)
- `category` (string)
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

#### Create Template

```http
POST /templates
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "template_type": "string",
  "file_path": "string",
  "file_format": "string",
  "content_structure": {},
  "category": "string",
  "tags": ["string"],
  "okpd2_codes": ["string"],
  "law_types": ["string"],
  "is_public": true,
  "version": "string"
}
```

#### Get Template

```http
GET /templates/{template_id}
```

#### Update Template

```http
PUT /templates/{template_id}
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "template_type": "string",
  "file_path": "string",
  "file_format": "string",
  "content_structure": {},
  "category": "string",
  "tags": ["string"],
  "okpd2_codes": ["string"],
  "law_types": ["string"],
  "is_public": true,
  "version": "string"
}
```

#### Delete Template

```http
DELETE /templates/{template_id}
```

### Knowledge Base

#### List Knowledge Base Entries

```http
GET /templates/knowledge-base
```

Query Parameters:
- `content_type` (string)
- `category` (string)
- `tags` (array[string])
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

#### Create Knowledge Base Entry

```http
POST /templates/knowledge-base
Content-Type: application/json

{
  "title": "string",
  "content_type": "string",
  "content": "string",
  "category": "string",
  "tags": ["string"],
  "okpd2_codes": ["string"],
  "keywords": ["string"],
  "related_templates": ["string"],
  "is_public": true
}
```

#### Get Knowledge Base Entry

```http
GET /templates/knowledge-base/{kb_id}
```

#### Update Knowledge Base Entry

```http
PUT /templates/knowledge-base/{kb_id}
Content-Type: application/json

{
  "title": "string",
  "content_type": "string",
  "content": "string",
  "category": "string",
  "tags": ["string"],
  "okpd2_codes": ["string"],
  "keywords": ["string"],
  "related_templates": ["string"],
  "is_public": true
}
```

#### Delete Knowledge Base Entry

```http
DELETE /templates/knowledge-base/{kb_id}
```

### Calendar

#### List Calendar Events

```http
GET /calendar/events
```

Query Parameters:
- `start_date` (datetime) - Required
- `end_date` (datetime) - Required
- `event_type` (string)
- `priority` (string)

#### Create Calendar Event

```http
POST /calendar/events
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "event_type": "string",
  "start_datetime": "2023-01-01T00:00:00Z",
  "end_datetime": "2023-01-01T01:00:00Z",
  "all_day": false,
  "location": "string",
  "priority": "normal",
  "status": "scheduled",
  "reminder_minutes_before": 0,
  "color": "string",
  "is_recurring": false,
  "recurrence_rule": {},
  "tender_id": "string",
  "task_id": "string"
}
```

#### Get Calendar Event

```http
GET /calendar/events/{event_id}
```

#### Update Calendar Event

```http
PUT /calendar/events/{event_id}
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "event_type": "string",
  "start_datetime": "2023-01-01T00:00:00Z",
  "end_datetime": "2023-01-01T01:00:00Z",
  "all_day": false,
  "location": "string",
  "priority": "normal",
  "status": "scheduled",
  "reminder_minutes_before": 0,
  "color": "string",
  "is_recurring": false,
  "recurrence_rule": {}
}
```

#### Delete Calendar Event

```http
DELETE /calendar/events/{event_id}
```

### Suppliers

#### List Suppliers

```http
GET /suppliers
```

Query Parameters:
- `name` (string)
- `specialization` (string)
- `region` (string)
- `min_reliability_rating` (number)
- `min_quality_rating` (number)
- `min_delivery_rating` (number)
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

#### Create Supplier

```http
POST /suppliers
Content-Type: application/json

{
  "name": "string",
  "inn": "string",
  "kpp": "string",
  "ogrn": "string",
  "legal_address": "string",
  "actual_address": "string",
  "phone": "string",
  "email": "string",
  "website": "string",
  "contact_person": "string",
  "specialization": ["string"],
  "regions_served": ["string"],
  "reliability_rating": 0,
  "quality_rating": 0,
  "delivery_rating": 0,
  "licenses": [{}],
  "certifications": [{}],
  "notes": "string"
}
```

#### Get Supplier

```http
GET /suppliers/{supplier_id}
```

#### Update Supplier

```http
PUT /suppliers/{supplier_id}
Content-Type: application/json

{
  "name": "string",
  "inn": "string",
  "kpp": "string",
  "ogrn": "string",
  "legal_address": "string",
  "actual_address": "string",
  "phone": "string",
  "email": "string",
  "website": "string",
  "contact_person": "string",
  "specialization": ["string"],
  "regions_served": ["string"],
  "reliability_rating": 0,
  "quality_rating": 0,
  "delivery_rating": 0,
  "licenses": [{}],
  "certifications": [{}],
  "notes": "string"
}
```

#### Delete Supplier

```http
DELETE /suppliers/{supplier_id}
```

### Risks

#### List Risks

```http
GET /risks
```

Query Parameters:
- `tender_id` (string)
- `risk_type` (string)
- `severity` (string)
- `probability` (string)
- `is_realized` (boolean)
- `mitigation_status` (string)
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

#### Create Risk

```http
POST /risks
Content-Type: application/json

{
  "tender_id": "string",
  "risk_type": "string",
  "title": "string",
  "description": "string",
  "severity": "string",
  "probability": "string",
  "impact_score": 0,
  "mitigation_strategy": "string",
  "detected_by": "string",
  "detection_details": {}
}
```

#### Get Risk

```http
GET /risks/{risk_id}
```

#### Update Risk

```http
PUT /risks/{risk_id}
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "severity": "string",
  "probability": "string",
  "impact_score": 0,
  "mitigation_strategy": "string",
  "mitigation_status": "string",
  "is_realized": true,
  "actual_impact": "string"
}
```

#### Delete Risk

```http
DELETE /risks/{risk_id}
```

### Collaboration

#### List Comments

```http
GET /collaboration/comments/tender/{tender_id}
```

Query Parameters:
- `include_replies` (boolean, default: true)

#### Create Comment

```http
POST /collaboration/comments
Content-Type: application/json

{
  "tender_id": "string",
  "content": "string",
  "parent_comment_id": "string",
  "mentioned_users": ["string"]
}
```

#### Get Comment

```http
GET /collaboration/comments/{comment_id}
```

#### Update Comment

```http
PUT /collaboration/comments/{comment_id}
Content-Type: application/json

{
  "content": "string"
}
```

#### Delete Comment

```http
DELETE /collaboration/comments/{comment_id}
```

### Import/Export

#### Import Data

```http
POST /import-export/import
Content-Type: application/json

{
  "entity_type": "string",
  "file_format": "string",
  "file_data": "string",
  "mapping": {},
  "options": {}
}
```

#### Export Data

```http
POST /import-export/export
Content-Type: application/json

{
  "entity_type": "string",
  "file_format": "string",
  "filters": {},
  "fields": ["string"],
  "options": {}
}
```

#### Get Import/Export Jobs

```http
GET /import-export/jobs/user
```

### Backup/Recovery

#### Create Backup

```http
POST /backup-recovery/backup
Content-Type: application/json

{
  "name": "string",
  "type": "full",
  "include_files": true,
  "include_database": true
}
```

#### List Backups

```http
GET /backup-recovery/backups
```

#### Restore from Backup

```http
POST /backup-recovery/restore
Content-Type: application/json

{
  "backup_path": "string",
  "restore_database": true,
  "restore_files": true
}
```

#### Verify Backup

```http
POST /backup-recovery/verify/{backup_path}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Anonymous requests**: 100 requests per hour
- **Authenticated requests**: 1000 requests per hour
- **Admin requests**: 5000 requests per hour

Exceeding these limits will result in a 429 (Too Many Requests) response.

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

Error responses include a JSON body with error details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## WebSockets

Real-time notifications are available via WebSocket connections:

### Connect

```
ws://your-domain.com/ws/notifications
```

Authentication is required with a JWT token in the query parameters:

```
ws://your-domain.com/ws/notifications?token=your_jwt_token
```

### Events

The WebSocket connection emits the following events:

- `notification_created` - New notification received
- `tender_updated` - Tender information updated
- `comment_created` - New comment added
- `task_assigned` - Task assigned to user

## SDKs and Libraries

Official SDKs are available for popular programming languages:

### Python

```bash
pip install tender-platform-sdk
```

```python
from tender_platform_sdk import TenderPlatformClient

client = TenderPlatformClient(
    base_url="https://your-domain.com/api/v1",
    api_key="your_api_key"
)

tenders = client.tenders.list()
```

### JavaScript

```bash
npm install @tender-platform/sdk
```

```javascript
import { TenderPlatformClient } from '@tender-platform/sdk';

const client = new TenderPlatformClient({
  baseUrl: 'https://your-domain.com/api/v1',
  apiKey: 'your_api_key'
});

const tenders = await client.tenders.list();
```

## Webhooks

Configure webhooks to receive real-time notifications of events:

### Set up Webhook

```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://your-endpoint.com/webhook",
  "events": ["tender_created", "tender_updated"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload

Webhooks are delivered as POST requests with JSON payloads:

```json
{
  "event": "tender_created",
  "timestamp": "2023-01-01T00:00:00Z",
  "data": {
    "tender": {
      "id": "uuid-here",
      "title": "New Tender",
      "budget": 1000000,
      "deadline": "2023-02-01T00:00:00Z"
    }
  },
  "signature": "hmac-sha256-signature"
}
```

### Signature Verification

Verify webhook authenticity by computing HMAC-SHA256 signature:

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

## Best Practices

### Authentication

- Store tokens securely and never in client-side code
- Use refresh tokens to maintain long-lived sessions
- Implement token expiration handling in your applications

### Rate Limiting

- Implement exponential backoff for rate-limited requests
- Cache responses when appropriate to reduce API calls
- Batch operations when possible

### Error Handling

- Always check HTTP status codes
- Implement retry logic for transient errors (500-series)
- Log errors for debugging and monitoring

### Security

- Use HTTPS in production environments
- Validate all inputs and sanitize outputs
- Implement proper access controls and permissions
- Rotate API keys regularly

For detailed information about each endpoint, parameters, and response formats, visit the interactive API documentation at `/docs` when the platform is running.