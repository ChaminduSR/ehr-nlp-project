# API Standards

These guidelines define the conventions for all API endpoints.

---

## 1. Endpoint Types

### 1.1 REST Endpoints (JSON)

**Use for**: Mobile apps, external integrations, or when structured data is needed.

**Convention**:
*   Return `Content-Type: application/json`
*   Use standard HTTP methods (GET, POST, PUT, DELETE)

**Example**:
```python
@patients_bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    # ... fetch patient ...
    return jsonify({
        'id': patient['id'],
        'mrn': patient['mrn'],
        'first_name': patient['first_name'],
        'last_name': patient['last_name'],
        'date_of_birth': patient['date_of_birth'],
        'created_at': patient['created_at']
    }), 200
```

---

### 1.2 HTMX Fragment Endpoints (HTML)

**Use for**: Frontend rendering, fast updates, reducing client-side JS.

**Convention**:
*   Suffix endpoint with `/fragment`
*   Return `Content-Type: text/html`
*   Use Jinja templates from `templates/fragments/`

**Example**:
```python
@joint_assessments_bp.route('/fragment', methods=['GET'])
def joint_assessment_fragment():
    # ... fetch data ...
    return render_template('fragments/joint_assessment.html', visit_id=visit_id)
```

---

## 2. URL Conventions

All API endpoints should be prefixed with `/api/v1`.

| Pattern | Example | Usage |
|---------|---------|-------|
| `/api/v1/<resource>` | `/api/v1/patients` | List/Create |
| `/api/v1/<resource>/<id>` | `/api/v1/patients/1` | Get/Update/Delete single |
| `/api/v1/<resource>/fragment` | `/api/v1/joint_assessments/fragment` | HTMX HTML fragment |
| `/api/v1/<resource>/<id>/<sub>` | `/api/v1/visits/1/notes` | Nested resources |

---

## 3. HTTP Methods

| Method | Action | Example |
|--------|--------|---------|
| GET | Read | `GET /patients/1` |
| POST | Create | `POST /patients` |
| PUT | Update (full) | `PUT /patients/1` |
| PATCH | Update (partial) | `PATCH /patients/1` |
| DELETE | Delete | `DELETE /patients/1` |

---

## 4. Request/Response Formats

### 4.1 Request Body (JSON)

```json
{
  "mrn": "MRN123456",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-05-15"
}
```

### 4.2 Success Response

```json
{
  "id": 1,
  "message": "Patient created"
}
```

### 4.3 Error Response

```json
{
  "error": "Patient not found"
}
```

### 4.4 List Response

```json
[
  { "id": 1, "mrn": "MRN001", "first_name": "John" },
  { "id": 2, "mrn": "MRN002", "first_name": "Jane" }
]
```

---

## 5. Date/Time Formats

*   **Date**: `YYYY-MM-DD` (e.g., `2025-12-02`)
*   **DateTime**: ISO 8601 (e.g., `2025-12-02T14:30:00Z`)
*   **Timezone**: Store in UTC, convert on client.

**Example**:
```python
from datetime import datetime

created_at = datetime.utcnow().isoformat() + 'Z'
# Result: "2025-12-02T14:30:00Z"
```

---

## 6. Pagination

### 6.1 Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Current page number |
| `per_page` | int | 15 | Items per page |
| `q` | string | "" | Search query |

**Example**: `GET /patients/fragment?page=2&per_page=15&q=smith`

### 6.2 Response Metadata

For fragment endpoints, include pagination data in template context:
```python
return render_template('fragments/patients_list.html',
    patients=patients,
    total_count=total_count,
    page=page,
    total_pages=total_pages,
    has_next=has_next,
    has_prev=has_prev,
    q=q
)
```

---

## 7. Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Not authorized |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Unexpected error |

---

## 8. Validation

### 8.1 Required Fields

Check for required fields and return 400 if missing:
```python
data = request.get_json()
if not data.get('mrn'):
    return jsonify({'error': 'MRN is required'}), 400
```

### 8.2 Type Validation

```python
try:
    patient_id = int(request.args.get('patient_id'))
except (ValueError, TypeError):
    return jsonify({'error': 'Invalid patient_id'}), 400
```

---

## 9. CORS

CORS is enabled globally in `app.py`:
```python
from flask_cors import CORS
CORS(app)
```

---

## 10. Health Check

Always provide a health check endpoint:
```python
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'environment': config.ENVIRONMENT,
        'version': '3.1'
    })
```

---

## 11. Reference

*   `routes/patients.py` - Example of REST + Fragment endpoints
*   `routes/visits.py` - Example of nested resource
*   `templates/fragments/` - HTMX fragment templates
