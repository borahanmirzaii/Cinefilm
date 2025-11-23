#!/bin/bash
set -e

PROJECT_ID="cinefilm-platform"
REGION="us-central1"

echo "🚀 Deploying to Production..."
echo ""
read -p "⚠️  Are you sure you want to deploy to PRODUCTION? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "❌ Deployment cancelled"
  exit 1
fi

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
  --tag gcr.io/$PROJECT_ID/backend:prod-$(git rev-parse --short HEAD) \
  --tag gcr.io/$PROJECT_ID/backend:latest

gcloud run deploy cinefilm-backend \
  --image gcr.io/$PROJECT_ID/backend:prod-$(git rev-parse --short HEAD) \
  --platform managed \
  --region $REGION \
  --service-account cinefilm-backend@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets=STRIPE_API_KEY=stripe-api-key:latest,STRIPE_WEBHOOK_SECRET=stripe-webhook-secret:latest \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 100 \
  --cpu 2 \
  --memory 2Gi

cd ..

# Get backend URL
BACKEND_URL=$(gcloud run services describe cinefilm-backend --region=$REGION --format="value(status.url)")

# Deploy frontend
echo ""
echo "📦 Building and deploying frontend..."
cd web-app

# Build with production API URL (static export for Firebase Hosting)
NEXT_PUBLIC_ENVIRONMENT=production \
NEXT_PUBLIC_API_URL=https://api.cinefilm.tech \
NEXT_OUTPUT=export \
pnpm build

# Deploy to Firebase
firebase deploy --only hosting:app --project $PROJECT_ID

cd ..

echo ""
echo "✅ Production deployment complete!"
echo "  • Frontend: https://cinefilm.tech"
echo "  • Backend:  $BACKEND_URL"
echo ""

