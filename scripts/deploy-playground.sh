#!/usr/bin/env bash
###############################################################################
# deploy-playground.sh — Build, push, and deploy the Math Content Engine
#                        playground to GCP Cloud Run.
#
# Usage:
#   ./scripts/deploy-playground.sh              # Deploy with defaults
#   ./scripts/deploy-playground.sh --env prod   # Deploy to production
#   ./scripts/deploy-playground.sh --skip-build # Re-deploy existing image
#   ./scripts/deploy-playground.sh --use-secrets # Use Secret Manager for keys
#   ./scripts/deploy-playground.sh --public     # Allow unauthenticated access
#   ./scripts/deploy-playground.sh --provider gemini    # Use Gemini (Vertex AI)
#   ./scripts/deploy-playground.sh --provider claude    # Use Claude (Anthropic)
#   ./scripts/deploy-playground.sh --provider deepseek  # Use DeepSeek (deepseek-reasoner)
#
# Prerequisites:
#   - gcloud CLI authenticated (gcloud auth login)
#   - Docker running locally
#   - Billing enabled on the GCP project
#   - For Claude: ANTHROPIC_API_KEY in .env
#   - For DeepSeek: DEEPSEEK_API_KEY in .env
#   - For Gemini: No API key needed (uses GCP service account on Cloud Run)
#
# Access:
#   By default, the service requires Google authentication (org members only).
#   Teammates access via browser — Google sign-in is handled automatically.
#   Use --public to allow unauthenticated access (requires org policy override).
###############################################################################
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration (override with environment variables)
# ---------------------------------------------------------------------------
PROJECT_ID="${GCP_PROJECT_ID:-lemonae}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${GCP_SERVICE_NAME:-math-playground}"
REPO_NAME="${GCP_REPO_NAME:-math-engine}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ENV_NAME="${ENV_NAME:-dev}"
ORG_DOMAIN="${GCP_ORG_DOMAIN:-lemonae.ai}"

# Cloud Run resource settings
CPU="${CLOUD_RUN_CPU:-4}"
MEMORY="${CLOUD_RUN_MEMORY:-4Gi}"
TIMEOUT="${CLOUD_RUN_TIMEOUT:-600}"
CONCURRENCY="${CLOUD_RUN_CONCURRENCY:-10}"
MIN_INSTANCES="${CLOUD_RUN_MIN_INSTANCES:-0}"
MAX_INSTANCES="${CLOUD_RUN_MAX_INSTANCES:-3}"

# LLM Provider (claude or gemini)
LLM_PROVIDER="${MATH_ENGINE_LLM_PROVIDER:-claude}"

# Flags
SKIP_BUILD=false
SKIP_PUSH=false
DRY_RUN=false
USE_SECRETS=false
PUBLIC_ACCESS=false

# Script directory (for resolving relative paths)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log()   { echo -e "${BLUE}[deploy]${NC} $*"; }
ok()    { echo -e "${GREEN}[  ok  ]${NC} $*"; }
warn()  { echo -e "${YELLOW}[ warn ]${NC} $*"; }
error() { echo -e "${RED}[error]${NC} $*" >&2; }

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)          ENV_NAME="$2"; shift 2 ;;
    --project)      PROJECT_ID="$2"; shift 2 ;;
    --region)       REGION="$2"; shift 2 ;;
    --service)      SERVICE_NAME="$2"; shift 2 ;;
    --tag)          IMAGE_TAG="$2"; shift 2 ;;
    --domain)       ORG_DOMAIN="$2"; shift 2 ;;
    --skip-build)   SKIP_BUILD=true; shift ;;
    --skip-push)    SKIP_PUSH=true; shift ;;
    --dry-run)      DRY_RUN=true; shift ;;
    --use-secrets)  USE_SECRETS=true; shift ;;
    --public)       PUBLIC_ACCESS=true; shift ;;
    --provider)     LLM_PROVIDER="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --env NAME        Environment name (default: dev)"
      echo "  --project ID      GCP project ID (default: lemonae)"
      echo "  --region REGION   GCP region (default: us-central1)"
      echo "  --service NAME    Cloud Run service name (default: math-playground)"
      echo "  --tag TAG         Docker image tag (default: latest)"
      echo "  --domain DOMAIN   Org domain for IAM access (default: lemonae.ai)"
      echo "  --skip-build      Skip Docker build, reuse existing image"
      echo "  --skip-push       Skip pushing to Artifact Registry"
      echo "  --use-secrets     Use GCP Secret Manager for API keys"
      echo "  --public          Allow unauthenticated access (requires org policy)"
      echo "  --provider NAME   LLM provider: claude, gemini, or deepseek (default: claude)"
      echo "  --dry-run         Print commands without executing"
      echo "  -h, --help        Show this help"
      exit 0
      ;;
    *) error "Unknown option: $1"; exit 1 ;;
  esac
done

# Derived values
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/playground:${IMAGE_TAG}"

# ---------------------------------------------------------------------------
# Helper: run or print command
# ---------------------------------------------------------------------------
run() {
  if $DRY_RUN; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
log "Pre-flight checks..."

# Check gcloud
if ! command -v gcloud &>/dev/null; then
  error "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
  exit 1
fi

# Check docker
if ! command -v docker &>/dev/null; then
  error "Docker not found. Install: https://docs.docker.com/get-docker/"
  exit 1
fi

# Verify gcloud auth
if ! gcloud projects describe "$PROJECT_ID" --format="value(projectId)" &>/dev/null; then
  error "Cannot access project '$PROJECT_ID'. Run: gcloud auth login"
  exit 1
fi

# Load .env for secrets
ENV_FILE="${PROJECT_ROOT}/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  error ".env file not found at $ENV_FILE"
  error "Copy .env.example to .env and set your ANTHROPIC_API_KEY"
  exit 1
fi

# Source .env to get API keys
set -a
source "$ENV_FILE"
set +a

# Validate provider choice
if [[ "$LLM_PROVIDER" != "claude" && "$LLM_PROVIDER" != "gemini" && "$LLM_PROVIDER" != "deepseek" ]]; then
  error "Invalid provider: $LLM_PROVIDER (must be 'claude', 'gemini', or 'deepseek')"
  exit 1
fi

# Validate API key for providers that require one
if [[ "$LLM_PROVIDER" == "claude" && -z "${ANTHROPIC_API_KEY:-}" ]]; then
  error "ANTHROPIC_API_KEY not set in .env (required for --provider claude)"
  exit 1
fi
if [[ "$LLM_PROVIDER" == "deepseek" && -z "${DEEPSEEK_API_KEY:-}" ]]; then
  error "DEEPSEEK_API_KEY not set in .env (required for --provider deepseek)"
  exit 1
fi

ok "Pre-flight checks passed (project=$PROJECT_ID, region=$REGION, provider=$LLM_PROVIDER)"

# ---------------------------------------------------------------------------
# Step 1: Enable required APIs
# ---------------------------------------------------------------------------
log "Step 1/7: Enabling required GCP APIs..."

APIS="run.googleapis.com artifactregistry.googleapis.com storage.googleapis.com"
if $USE_SECRETS; then
  APIS="$APIS secretmanager.googleapis.com"
fi
if [[ "$LLM_PROVIDER" == "gemini" ]]; then
  APIS="$APIS aiplatform.googleapis.com"
fi

run gcloud services enable $APIS --project="$PROJECT_ID" --quiet

ok "APIs enabled"

# ---------------------------------------------------------------------------
# Step 2: Create Artifact Registry repository (if needed)
# ---------------------------------------------------------------------------
log "Step 2/7: Ensuring Artifact Registry repository exists..."
if ! gcloud artifacts repositories describe "$REPO_NAME" \
     --location="$REGION" --project="$PROJECT_ID" &>/dev/null 2>&1; then
  log "Creating Artifact Registry repository: $REPO_NAME"
  run gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --project="$PROJECT_ID" \
    --description="Math Content Engine images"
  ok "Repository created"
else
  ok "Repository already exists"
fi

# ---------------------------------------------------------------------------
# Step 2b: Create GCS bucket for prompt storage (if needed)
# ---------------------------------------------------------------------------
PROMPT_BUCKET="${PROMPT_STORAGE_BUCKET:-lemonae-prompt-sessions}"
log "Ensuring GCS bucket exists: gs://${PROMPT_BUCKET} ..."

if ! gcloud storage buckets describe "gs://${PROMPT_BUCKET}" --project="$PROJECT_ID" &>/dev/null 2>&1; then
  log "Creating GCS bucket: gs://${PROMPT_BUCKET}"
  run gcloud storage buckets create "gs://${PROMPT_BUCKET}" \
    --project="$PROJECT_ID" \
    --location="$REGION" \
    --uniform-bucket-level-access
  ok "GCS bucket created: gs://${PROMPT_BUCKET}"
else
  ok "GCS bucket already exists: gs://${PROMPT_BUCKET}"
fi

# Grant the Cloud Run service account access to the bucket
PROJECT_NUMBER_FOR_BUCKET=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
BUCKET_SA="${PROJECT_NUMBER_FOR_BUCKET}-compute@developer.gserviceaccount.com"
run gcloud storage buckets add-iam-policy-binding "gs://${PROMPT_BUCKET}" \
  --member="serviceAccount:${BUCKET_SA}" \
  --role="roles/storage.objectAdmin" \
  --quiet 2>/dev/null || true
ok "Storage access granted to Cloud Run service account"

# ---------------------------------------------------------------------------
# Step 3+4: Build & push Docker image (linux/amd64 for Cloud Run)
# ---------------------------------------------------------------------------
if ! $SKIP_BUILD; then
  log "Step 3/7: Building Docker image (linux/amd64)..."
  log "Step 4/7: Pushing image to Artifact Registry..."

  # Configure Docker auth for Artifact Registry
  run gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

  # Cloud Run requires amd64. Use buildx to cross-compile on Apple Silicon.
  # Use --push (not --load) to push directly to registry, avoiding Docker
  # Desktop's read-only filesystem bug with local metadata writes.
  run docker buildx build \
    --platform linux/amd64 \
    -t "$IMAGE_URI" \
    -f "$PROJECT_ROOT/docker/Dockerfile.engine" \
    --push \
    "$PROJECT_ROOT"
  ok "Image built and pushed: $IMAGE_URI"
else
  warn "Skipping build (--skip-build)"
  if ! $SKIP_PUSH; then
    log "Step 4/7: Pushing image to Artifact Registry..."
    run gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
    run docker push "$IMAGE_URI"
    ok "Image pushed: $IMAGE_URI"
  else
    warn "Skipping push (--skip-push)"
  fi
fi

# ---------------------------------------------------------------------------
# Step 5: Deploy to Cloud Run
# ---------------------------------------------------------------------------
log "Step 5/7: Deploying to Cloud Run..."

# Build env vars string for Cloud Run (non-secret values)
ENV_VARS="ENVIRONMENT=${ENV_NAME}"
ENV_VARS="${ENV_VARS},MATH_ENGINE_LLM_PROVIDER=${LLM_PROVIDER}"
ENV_VARS="${ENV_VARS},MATH_ENGINE_VIDEO_QUALITY=${MATH_ENGINE_VIDEO_QUALITY:-m}"
ENV_VARS="${ENV_VARS},MATH_ENGINE_MAX_RETRIES=${MATH_ENGINE_MAX_RETRIES:-5}"
ENV_VARS="${ENV_VARS},MATH_ENGINE_TEMPERATURE=${MATH_ENGINE_TEMPERATURE:-0}"
ENV_VARS="${ENV_VARS},MATH_ENGINE_MAX_TOKENS=${MATH_ENGINE_MAX_TOKENS:-4096}"

# Provider-specific model config
if [[ "$LLM_PROVIDER" == "claude" && -n "${MATH_ENGINE_CLAUDE_MODEL:-}" ]]; then
  ENV_VARS="${ENV_VARS},MATH_ENGINE_CLAUDE_MODEL=${MATH_ENGINE_CLAUDE_MODEL}"
fi
if [[ "$LLM_PROVIDER" == "gemini" ]]; then
  ENV_VARS="${ENV_VARS},MATH_ENGINE_GEMINI_MODEL=${MATH_ENGINE_GEMINI_MODEL:-gemini-2.0-flash}"
  ENV_VARS="${ENV_VARS},GCP_LOCATION=${REGION}"
fi
if [[ "$LLM_PROVIDER" == "deepseek" ]]; then
  ENV_VARS="${ENV_VARS},MATH_ENGINE_DEEPSEEK_MODEL=${MATH_ENGINE_DEEPSEEK_MODEL:-deepseek-reasoner}"
fi

# Prompt storage bucket
ENV_VARS="${ENV_VARS},PROMPT_STORAGE_BUCKET=${PROMPT_BUCKET}"
ENV_VARS="${ENV_VARS},GCP_PROJECT_ID=${PROJECT_ID}"

# Mathpix (optional)
if [[ -n "${MATHPIX_APP_ID:-}" ]]; then
  ENV_VARS="${ENV_VARS},MATHPIX_APP_ID=${MATHPIX_APP_ID}"
fi
if [[ -n "${MATHPIX_APP_KEY:-}" ]]; then
  ENV_VARS="${ENV_VARS},MATHPIX_APP_KEY=${MATHPIX_APP_KEY}"
fi

# Build the deploy command
# --no-cpu-throttling keeps CPU allocated between requests so that
# background tasks (Manim rendering, LLM calls via asyncio.to_thread)
# aren't killed when no HTTP request is active.
DEPLOY_ARGS=(
  gcloud run deploy "$SERVICE_NAME"
  --image="$IMAGE_URI"
  --region="$REGION"
  --project="$PROJECT_ID"
  --platform=managed
  --cpu="$CPU"
  --memory="$MEMORY"
  --timeout="$TIMEOUT"
  --concurrency="$CONCURRENCY"
  --min-instances="$MIN_INSTANCES"
  --max-instances="$MAX_INSTANCES"
  --no-cpu-throttling
  --quiet
)

if $PUBLIC_ACCESS; then
  DEPLOY_ARGS+=(--allow-unauthenticated)
else
  DEPLOY_ARGS+=(--no-allow-unauthenticated)
fi

if [[ "$LLM_PROVIDER" == "gemini" ]]; then
  # Gemini uses Vertex AI with ADC — no API key needed on Cloud Run.
  # Just grant the Cloud Run service account the Vertex AI User role.
  DEPLOY_ARGS+=(--set-env-vars="$ENV_VARS")

elif [[ "$LLM_PROVIDER" == "deepseek" ]]; then
  # DeepSeek requires an API key — pass as env var (same pattern as Claude)
  ENV_VARS="${ENV_VARS},DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}"
  DEPLOY_ARGS+=(--set-env-vars="$ENV_VARS")

elif $USE_SECRETS; then
  # Create secret if it doesn't exist, then set its value
  if ! gcloud secrets describe anthropic-api-key --project="$PROJECT_ID" &>/dev/null 2>&1; then
    log "Creating secret 'anthropic-api-key' in Secret Manager..."
    run printf '%s' "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key \
      --data-file=- --project="$PROJECT_ID"
  else
    log "Updating secret 'anthropic-api-key'..."
    run printf '%s' "$ANTHROPIC_API_KEY" | gcloud secrets versions add anthropic-api-key \
      --data-file=- --project="$PROJECT_ID"
  fi

  # Grant Cloud Run service agent access to the secret
  PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
  run gcloud secrets add-iam-policy-binding anthropic-api-key \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID" --quiet

  DEPLOY_ARGS+=(
    --set-env-vars="$ENV_VARS"
    --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest"
  )
else
  # Pass API key directly as env var (simpler, fine for dev)
  ENV_VARS="${ENV_VARS},ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"
  DEPLOY_ARGS+=(--set-env-vars="$ENV_VARS")
fi

run "${DEPLOY_ARGS[@]}"

ok "Deployed to Cloud Run"

# ---------------------------------------------------------------------------
# Step 5b: Grant Vertex AI access for Gemini provider
# ---------------------------------------------------------------------------
if [[ "$LLM_PROVIDER" == "gemini" ]]; then
  log "Granting Vertex AI access to Cloud Run service account..."
  PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
  SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  run gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA}" \
    --role="roles/aiplatform.user" \
    --quiet 2>/dev/null || true
  ok "Vertex AI User role granted to ${SA}"
fi

# ---------------------------------------------------------------------------
# Step 6: Set IAM for org domain access
# ---------------------------------------------------------------------------
if ! $PUBLIC_ACCESS; then
  log "Step 6/7: Granting access to ${ORG_DOMAIN} members..."
  run gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --member="domain:${ORG_DOMAIN}" \
    --role=roles/run.invoker 2>/dev/null || true
  ok "IAM policy updated — ${ORG_DOMAIN} members can access the service"
else
  log "Step 6/7: Public access enabled (--allow-unauthenticated)"
fi

# ---------------------------------------------------------------------------
# Step 7: Get service URL and verify
# ---------------------------------------------------------------------------
log "Step 7/7: Verifying deployment..."

if ! $DRY_RUN; then
  SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)")

  # Health check with retry (use auth token since service is authenticated)
  log "Running health check (may take ~15s for cold start)..."
  AUTH_HEADER=""
  if ! $PUBLIC_ACCESS; then
    AUTH_HEADER="Authorization: Bearer $(gcloud auth print-identity-token)"
  fi

  for i in 1 2 3; do
    if [[ -n "$AUTH_HEADER" ]]; then
      HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "${SERVICE_URL}/health" --max-time 30 || echo "000")
    else
      HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}/health" --max-time 30 || echo "000")
    fi
    if [[ "$HTTP_STATUS" == "200" ]]; then
      break
    fi
    if [[ $i -lt 3 ]]; then
      log "Attempt $i: HTTP $HTTP_STATUS, retrying in 10s..."
      sleep 10
    fi
  done

  if [[ "$HTTP_STATUS" == "200" ]]; then
    ok "Health check passed"
  else
    warn "Health check returned HTTP $HTTP_STATUS (service may still be starting)"
  fi

  echo ""
  echo "==========================================================================="
  echo -e "${GREEN}Deployment complete!${NC}"
  echo "==========================================================================="
  echo ""
  echo "  Service URL:    $SERVICE_URL"
  echo "  Playground:     ${SERVICE_URL}/playground/"
  echo "  API Docs:       ${SERVICE_URL}/docs"
  echo "  Health Check:   ${SERVICE_URL}/health"
  echo ""
  echo "  Project:        $PROJECT_ID"
  echo "  Region:         $REGION"
  echo "  Service:        $SERVICE_NAME"
  echo "  Image:          $IMAGE_URI"
  echo "  LLM Provider:   $LLM_PROVIDER"
  if [[ "$LLM_PROVIDER" == "gemini" ]]; then
    echo "  Gemini Model:   ${MATH_ENGINE_GEMINI_MODEL:-gemini-2.0-flash}"
    echo "  Auth:           Vertex AI (ADC — no API key)"
  elif [[ "$LLM_PROVIDER" == "deepseek" ]]; then
    echo "  DeepSeek Model: ${MATH_ENGINE_DEEPSEEK_MODEL:-deepseek-reasoner}"
  else
    echo "  Claude Model:   ${MATH_ENGINE_CLAUDE_MODEL:-claude-sonnet-4-20250514}"
  fi
  if ! $PUBLIC_ACCESS; then
    echo ""
    echo "  Access:         Authenticated (${ORG_DOMAIN} members)"
    echo "  Note:           Teammates open the URL in a browser and sign in"
    echo "                  with their @${ORG_DOMAIN} Google account."
  fi
  echo ""
  echo "==========================================================================="
else
  echo ""
  echo "[dry-run] Would deploy to Cloud Run and output service URL"
fi
