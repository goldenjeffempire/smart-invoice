# 🔌 Smart Invoice API Documentation

**Version:** 2.0.0  
**Base URL:** `https://your-domain.com`  
**Authentication:** Session-based (Django Auth)

---

## 📑 Table of Contents

1. [Authentication](#authentication)
2. [Payment Endpoints](#payment-endpoints)
3. [Webhook Endpoints](#webhook-endpoints)
4. [Export Endpoints](#export-endpoints)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Testing](#testing)

---

## 🔐 Authentication

All API endpoints (except webhooks) require authentication via Django session cookies. Users must be logged in to access invoice and payment endpoints.

### Login Endpoint
```http
POST /login/
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response:**
- `302 Redirect` to dashboard on success
- `200 OK` with form errors on failure

---

## 💳 Payment Endpoints

### 1. Create Paystack Checkout

Creates a payment checkout link for an invoice using Paystack.

**Endpoint:** `POST /api/invoices/<invoice_id>/create-paystack-checkout/`  
**Authentication:** Required  
**Rate Limit:** 60 requests/minute

#### Request

```http
POST /api/invoices/123/create-paystack-checkout/
Content-Type: application/json
Cookie: sessionid=<session_cookie>
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "checkout_url": "https://checkout.paystack.com/abc123xyz",
  "reference": "INV-A1B2C3D4-20251024153045",
  "invoice_id": "INV-A1B2C3D4",
  "amount": 150000.00,
  "currency": "NGN"
}
```

#### Error Responses

**Invoice Not Found (404)**
```json
{
  "success": false,
  "error": "Invoice not found"
}
```

**Unauthorized Access (403)**
```json
{
  "success": false,
  "error": "You do not have permission to access this invoice"
}
```

**Paystack Configuration Missing (500)**
```json
{
  "success": false,
  "error": "Paystack is not configured. Please contact support."
}
```

**Paystack API Error (500)**
```json
{
  "success": false,
  "error": "Failed to create payment link: <error_details>"
}
```

#### Implementation Example

**JavaScript (Frontend)**
```javascript
async function createPaymentLink(invoiceId) {
  try {
    const response = await fetch(`/api/invoices/${invoiceId}/create-paystack-checkout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      credentials: 'include'
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Open payment link
      window.open(data.checkout_url, '_blank');
    } else {
      console.error('Payment error:', data.error);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}
```

**Python**
```python
import requests

url = f'https://your-domain.com/api/invoices/{invoice_id}/create-paystack-checkout/'
cookies = {'sessionid': 'your_session_cookie'}

response = requests.post(url, cookies=cookies)
data = response.json()

if data['success']:
    checkout_url = data['checkout_url']
    print(f"Payment link: {checkout_url}")
```

---

### 2. Payment Callback

Handles redirect after successful/failed Paystack payment.

**Endpoint:** `GET /payment/callback/`  
**Authentication:** Not Required (public)  
**Rate Limit:** 60 requests/minute

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `reference` | string | Yes | Paystack transaction reference |
| `trxref` | string | No | Alternative reference parameter |

#### Request Example

```http
GET /payment/callback/?reference=INV-A1B2C3D4-20251024153045
```

#### Behavior

1. Verifies payment with Paystack API
2. Updates invoice status to `paid` if payment successful
3. Creates `PaymentTransaction` record
4. Displays success/failure page to user

#### Response

**Success:** Renders `payment_callback.html` with success message  
**Failure:** Renders `payment_callback.html` with error message

---

## 🪝 Webhook Endpoints

### Paystack Webhook

Receives payment notification events from Paystack.

**Endpoint:** `POST /api/paystack/webhook/`  
**Authentication:** HMAC Signature Verification  
**Rate Limit:** None (webhooks)

#### Security

All webhook requests MUST include a valid `X-Paystack-Signature` header. The signature is validated using HMAC-SHA512:

```python
import hmac
import hashlib

def verify_signature(payload: str, signature: str, secret: str) -> bool:
    computed = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature)
```

#### Headers

```http
X-Paystack-Signature: <hmac_sha512_signature>
Content-Type: application/json
```

#### Supported Events

| Event | Description |
|-------|-------------|
| `charge.success` | Payment completed successfully |
| `charge.failed` | Payment failed |

#### Request Payload Example

```json
{
  "event": "charge.success",
  "data": {
    "reference": "INV-A1B2C3D4-20251024153045",
    "amount": 15000000,
    "currency": "NGN",
    "status": "success",
    "paid_at": "2025-10-24T15:45:30.000Z",
    "customer": {
      "email": "customer@example.com"
    },
    "metadata": {
      "invoice_id": "INV-A1B2C3D4"
    }
  }
}
```

#### Success Response (200 OK)

```json
{
  "status": "success"
}
```

#### Error Responses

**Invalid Signature (403)**
```json
{
  "error": "Invalid signature"
}
```

**Unsupported Event (400)**
```json
{
  "error": "Unsupported event type: <event_name>"
}
```

**Invoice Not Found (404)**
```json
{
  "error": "Invoice not found"
}
```

**Duplicate Event (200)** *(Idempotent Response)*
```json
{
  "status": "already_processed"
}
```

#### Idempotency

The webhook endpoint handles duplicate events gracefully:
- If a `charge.success` event is received multiple times, it will only update the invoice once
- Subsequent calls return `200 OK` with `already_processed` status
- This prevents duplicate invoice status updates

#### Testing Webhooks Locally

Use [ngrok](https://ngrok.com/) to expose your local server:

```bash
# 1. Start your local server
python manage.py runserver 0.0.0.0:5000

# 2. Start ngrok
ngrok http 5000

# 3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

# 4. Configure in Paystack Dashboard:
# Webhook URL: https://abc123.ngrok.io/api/paystack/webhook/
```

#### Webhook Debugging

Enable detailed logging in your settings:

```python
LOGGING = {
    'loggers': {
        'invoices': {
            'level': 'DEBUG',
        },
    },
}
```

Check webhook logs:
```bash
# Development
tail -f logs/django.log | grep webhook

# Docker
docker-compose logs -f web | grep webhook

# Render/Heroku
# View logs in platform dashboard
```

---

## 📤 Export Endpoints

### 1. Export Invoices to CSV

**Endpoint:** `GET /invoices/export/csv/`  
**Authentication:** Required  
**Rate Limit:** 10 requests/minute

#### Response

```http
200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename="invoices_20251024.csv"

Invoice ID,Client Name,Amount,Currency,Status,Issue Date,Due Date
INV-A1B2C3D4,John Doe,1500.00,USD,paid,2025-10-20,2025-11-20
INV-E5F6G7H8,Jane Smith,2500.00,NGN,sent,2025-10-22,2025-11-22
```

### 2. Export Payments to CSV

**Endpoint:** `GET /payments/export/csv/`  
**Authentication:** Required  
**Rate Limit:** 10 requests/minute

### 3. Export Clients to CSV

**Endpoint:** `GET /clients/export/csv/`  
**Authentication:** Required  
**Rate Limit:** 10 requests/minute

---

## 🚨 Error Handling

### Standard Error Response Format

```json
{
  "success": false,
  "error": "Error message here",
  "details": {
    "field_name": ["Error detail 1", "Error detail 2"]
  }
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Request successful |
| 302 | Redirect | After form submission |
| 400 | Bad Request | Invalid input data |
| 403 | Forbidden | Authentication failed or insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal error (check logs) |

---

## 🛡️ Rate Limiting

Protected endpoints have rate limiting to prevent abuse:

| Endpoint Pattern | Limit | Window |
|------------------|-------|--------|
| `/login/` | 60 requests | 60 seconds |
| `/signup/` | 60 requests | 60 seconds |
| `/invoice/pay/` | 60 requests | 60 seconds |
| `/payment/callback/` | 60 requests | 60 seconds |

**Rate Limit Response (429):**
```http
HTTP/1.1 429 Too Many Requests
Content-Type: text/html

Rate limit exceeded. Please try again later.
```

---

## 🧪 Testing

### Test with cURL

**Create Paystack Checkout:**
```bash
curl -X POST https://your-domain.com/api/invoices/123/create-paystack-checkout/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  --cookie "sessionid=your-session-cookie"
```

**Test Webhook (with signature):**
```bash
# Calculate signature
PAYLOAD='{"event":"charge.success","data":{"reference":"TEST-REF","amount":100000}}'
SECRET="your-webhook-secret"
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha512 -hmac "$SECRET" | awk '{print $2}')

# Send request
curl -X POST https://your-domain.com/api/paystack/webhook/ \
  -H "Content-Type: application/json" \
  -H "X-Paystack-Signature: $SIGNATURE" \
  -d "$PAYLOAD"
```

### Automated Testing

```bash
# Run API tests
pytest invoices/tests/test_api_endpoints.py -v

# Run webhook tests
pytest invoices/tests/test_webhooks.py -v

# Run all tests with coverage
pytest --cov=invoices --cov-report=html
```

---

## 📞 Support

- **Documentation Issues:** Open GitHub issue
- **Integration Help:** Contact via support form at `/support/`
- **Security Issues:** Email security@your-domain.com

---

**Built with ❤️ by Jeffery Onome** | [Portfolio](https://onome-portfolio-ten.vercel.app)
