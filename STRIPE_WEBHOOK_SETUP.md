# 🔗 Stripe Webhook Setup Guide

**Status**: Stripe CLI installed ✅  
**Next**: Authenticate → Create webhook → Get secret

---

## Step 1: Authenticate Stripe CLI

```bash
stripe login
```

This will open your browser to authenticate.

---

## Step 2: Create Webhook Endpoint

After authentication, create a webhook endpoint:

```bash
# For local testing (development)
stripe listen --forward-to http://localhost:8000/api/webhooks/stripe

# For production (after deployment)
stripe webhook-endpoints create \
  --url https://yourdomain.com/api/webhooks/stripe \
  --enabled-events payment_intent.succeeded \
  --enabled-events customer.subscription.created \
  --enabled-events customer.subscription.updated \
  --enabled-events customer.subscription.deleted \
  --enabled-events invoice.payment_succeeded \
  --enabled-events invoice.payment_failed
```

---

## Step 3: Get Webhook Signing Secret

### Option A: From Stripe CLI (Local Testing)

When you run `stripe listen`, it will show:
```
> Ready! Your webhook signing secret is whsec_xxxxx
```

### Option B: From Stripe Dashboard

1. Go to: https://dashboard.stripe.com/webhooks
2. Click on your webhook endpoint
3. Click "Reveal" next to "Signing secret"
4. Copy the secret (starts with `whsec_`)

### Option C: Via Stripe CLI

```bash
# List webhooks
stripe webhook-endpoints list

# Get signing secret for a specific webhook
stripe webhook-endpoints retrieve WEBHOOK_ID
```

---

## Step 4: Store Secret in Google Cloud

Once you have the signing secret:

```bash
echo -n "whsec_YOUR_SECRET_HERE" | gcloud secrets create stripe-webhook-secret \
  --data-file=- \
  --replication-policy="automatic" \
  --project=cinefilm-platform
```

---

## Step 5: Verify Secret

```bash
gcloud secrets list --project=cinefilm-platform --filter="name~stripe"
```

Should show:
- `stripe-api-key`
- `stripe-publishable-key`
- `stripe-secret-key`
- `stripe-webhook-secret` ✅

---

## Quick Commands Summary

```bash
# 1. Authenticate
stripe login

# 2. Create webhook (production)
stripe webhook-endpoints create \
  --url https://yourdomain.com/api/webhooks/stripe \
  --enabled-events payment_intent.succeeded customer.subscription.created

# 3. Get signing secret (from dashboard or CLI output)
# Copy the whsec_xxxxx value

# 4. Store in Google Cloud
echo -n "whsec_YOUR_SECRET" | gcloud secrets create stripe-webhook-secret \
  --data-file=- --replication-policy="automatic" --project=cinefilm-platform

# 5. Verify
gcloud secrets list --project=cinefilm-platform --filter="name~stripe"
```

---

## Testing Webhooks Locally

For local development:

```bash
# Terminal 1: Start your backend
cd backend
uv run uvicorn api.main:app --reload

# Terminal 2: Forward Stripe webhooks to local backend
stripe listen --forward-to http://localhost:8000/api/webhooks/stripe
```

This will show webhook events in real-time and forward them to your local backend.

---

**Status**: Ready for authentication  
**Next**: Run `stripe login` → Follow steps above

