#!/usr/bin/env bash
# Deploy the NewMovies weekly digest to GCP (Cloud Run Job + Cloud Scheduler).
# Run from the project root, after billing is linked. Requires: gcloud, docker (buildx).
set -euo pipefail

PROJECT="newmovies-digest"
REGION="us-west1"
REPO="newmovies"
JOB="newmovies-digest"
SCHED="newmovies-weekly"
SCHEDULE="0 17 * * 5"
TIMEZONE="America/Los_Angeles"
SA_NAME="newmovies-job"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
BUCKET="${PROJECT}-state"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/newmovies:latest"

# Secret + recipient values come from .env (gitignored).
set -a; . ./.env; set +a

echo "==> Enable APIs"
gcloud services enable run.googleapis.com cloudscheduler.googleapis.com \
  secretmanager.googleapis.com artifactregistry.googleapis.com \
  storage.googleapis.com --project="$PROJECT"

echo "==> Artifact Registry repo + keep-latest-only cleanup policy"
gcloud artifacts repositories describe "$REPO" --location="$REGION" --project="$PROJECT" >/dev/null 2>&1 \
  || gcloud artifacts repositories create "$REPO" --repository-format=docker \
       --location="$REGION" --project="$PROJECT" --description="NewMovies digest images"
gcloud artifacts repositories set-cleanup-policies "$REPO" --location="$REGION" \
  --project="$PROJECT" --policy=cleanup-policy.json --no-dry-run

echo "==> State bucket (GCS)"
gcloud storage buckets describe "gs://${BUCKET}" >/dev/null 2>&1 \
  || gcloud storage buckets create "gs://${BUCKET}" --location="$REGION" \
       --project="$PROJECT" --uniform-bucket-level-access

echo "==> Service account + IAM"
gcloud iam service-accounts describe "$SA" --project="$PROJECT" >/dev/null 2>&1 \
  || gcloud iam service-accounts create "$SA_NAME" --project="$PROJECT" \
       --display-name="NewMovies digest job"
gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --member="serviceAccount:${SA}" --role="roles/storage.objectAdmin" >/dev/null
gcloud projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:${SA}" --role="roles/run.invoker" >/dev/null

echo "==> Secrets"
upsert_secret () {
  local name="$1" value="$2"
  if gcloud secrets describe "$name" --project="$PROJECT" >/dev/null 2>&1; then
    printf '%s' "$value" | gcloud secrets versions add "$name" --project="$PROJECT" --data-file=-
  else
    printf '%s' "$value" | gcloud secrets create "$name" --project="$PROJECT" --data-file=-
  fi
  gcloud secrets add-iam-policy-binding "$name" --project="$PROJECT" \
    --member="serviceAccount:${SA}" --role="roles/secretmanager.secretAccessor" >/dev/null
}
upsert_secret tmdb-token "$TMDB_TOKEN"
upsert_secret gmail-app-password "$GMAIL_APP_PASSWORD"

echo "==> Build & push image (linux/amd64)"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
docker buildx build --platform linux/amd64 -t "$IMAGE" --push .

echo "==> Cloud Run Job"
# ^@@^ sets '@@' as the list delimiter so commas inside EMAIL_TO aren't split.
gcloud run jobs deploy "$JOB" --project="$PROJECT" --region="$REGION" \
  --image="$IMAGE" --service-account="$SA" --max-retries=1 --task-timeout=300s \
  --set-env-vars="^@@^STATE_BACKEND=gcs@@STATE_GCS_BUCKET=${BUCKET}@@STATE_GCS_OBJECT=state.json@@GMAIL_ADDRESS=${GMAIL_ADDRESS}@@EMAIL_TO=${EMAIL_TO}@@REGION=US@@WINDOW_DAYS=14@@MIN_POPULARITY=10@@SEND_WHEN_EMPTY=true" \
  --set-secrets="TMDB_TOKEN=tmdb-token:latest,GMAIL_APP_PASSWORD=gmail-app-password:latest"

echo "==> Cloud Scheduler (Fri 17:00 ${TIMEZONE})"
URI="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT}/jobs/${JOB}:run"
if gcloud scheduler jobs describe "$SCHED" --location="$REGION" --project="$PROJECT" >/dev/null 2>&1; then
  ACTION=update
else
  ACTION=create
fi
gcloud scheduler jobs "$ACTION" http "$SCHED" --project="$PROJECT" --location="$REGION" \
  --schedule="$SCHEDULE" --time-zone="$TIMEZONE" \
  --uri="$URI" --http-method=POST --oauth-service-account-email="$SA"

echo
echo "Deployed. Trigger a manual run with:"
echo "  gcloud run jobs execute ${JOB} --region=${REGION} --project=${PROJECT}"
