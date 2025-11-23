#!/bin/bash
set -e

echo "🧹 Cleaning up old Cloud Run services..."

PROJECT_ID="cinefilm-platform"
REGION="us-central1"

# Delete old Cloud Run services
echo "Deleting backend-api..."
gcloud run services delete backend-api --region=$REGION --quiet || echo "Service not found"

echo "Deleting main-frontend..."
gcloud run services delete main-frontend --region=$REGION --quiet || echo "Service not found"

echo "Deleting db-migration job..."
gcloud run jobs delete db-migration --region=$REGION --quiet || echo "Job not found"

# List any remaining services
echo ""
echo "Remaining Cloud Run services:"
gcloud run services list --region=$REGION || echo "No services found"

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "⚠️ Storage buckets were NOT deleted. Review manually:"
echo "  gsutil ls"
echo ""

