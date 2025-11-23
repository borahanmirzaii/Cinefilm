#!/bin/bash
set -e

PROJECT_ID="cinefilm-platform"
REGION="us-central1"

echo "🚀 Deploying to Staging..."
echo ""

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
  echo "❌ Not authenticated to gcloud. Run: gcloud auth login"
  exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Deploy backend
echo "📦 Building and deploying backend..."
cd backend
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD) \
  --tag gcr.io/$PROJECT_ID/backend:staging-$(git rev-parse --short HEAD)

gcloud run deploy cinefilm-backend-staging \
  --image gcr.io/$PROJECT_ID/backend:staging-$(git rev-parse --short HEAD) \
  --platform managed \
  --region $REGION \
  --service-account cinefilm-backend@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars ENVIRONMENT=staging \
  --set-secrets=STRIPE_API_KEY=stripe-api-key:latest,STRIPE_WEBHOOK_SECRET=stripe-webhook-secret:latest \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 10

cd ..

# Get backend URL
BACKEND_URL=$(gcloud run services describe cinefilm-backend-staging --region=$REGION --format="value(status.url)")

# Deploy frontend
echo ""
echo "📦 Building and deploying frontend..."
cd web-app

# Build with staging API URL (static export for Firebase Hosting)
NEXT_PUBLIC_ENVIRONMENT=staging \
NEXT_PUBLIC_API_URL=$BACKEND_URL \
NEXT_OUTPUT=export \
pnpm build

# Deploy to Firebase
firebase deploy --only hosting:staging --project $PROJECT_ID

cd ..

echo ""
echo "✅ Staging deployment complete!"
echo "  • Frontend: https://staging.cinefilm.tech"
echo "  • Backend:  $BACKEND_URL"
echo ""

