#!/bin/bash

# IntegMed - AWS Cloud Deployment Script
# Deploys to AWS EKS (Elastic Kubernetes Service)

set -e

echo "☁️  IntegMed - AWS Cloud Deployment"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
AWS_REGION=${AWS_REGION:-"ap-south-1"}  # Mumbai
CLUSTER_NAME=${CLUSTER_NAME:-"integmed-prod"}
NAMESPACE="integmed-prod"
ECR_REPO_PREFIX="integmed"

echo "📋 Configuration:"
echo "   AWS Region: $AWS_REGION"
echo "   Cluster: $CLUSTER_NAME"
echo "   Namespace: $NAMESPACE"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not installed${NC}"
    echo "Install: https://aws.amazon.com/cli/"
    exit 1
fi
echo -e "${GREEN}✓${NC} AWS CLI"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not installed${NC}"
    echo "Install: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo -e "${GREEN}✓${NC} kubectl"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker"

echo ""
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓${NC} AWS Account: $AWS_ACCOUNT_ID"

echo ""
echo "📦 Step 1: Building and pushing Docker images..."

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Create ECR repositories if they don't exist
for repo in backend frontend; do
    aws ecr describe-repositories --repository-names $ECR_REPO_PREFIX/$repo --region $AWS_REGION &> /dev/null || \
        aws ecr create-repository --repository-name $ECR_REPO_PREFIX/$repo --region $AWS_REGION
done

# Build and push backend
echo "Building backend image..."
docker build -t $ECR_REPO_PREFIX/backend:latest --target production -f backend/Dockerfile backend/
docker tag $ECR_REPO_PREFIX/backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_PREFIX/backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_PREFIX/backend:latest

# Build and push frontend
echo "Building frontend image..."
docker build -t $ECR_REPO_PREFIX/frontend:latest --target production -f frontend/Dockerfile frontend/
docker tag $ECR_REPO_PREFIX/frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_PREFIX/frontend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_PREFIX/frontend:latest

echo -e "${GREEN}✓${NC} Images pushed to ECR"

echo ""
echo "🎯 Step 2: Configuring kubectl for EKS..."

# Update kubeconfig
aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME

# Verify connection
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Cannot connect to cluster${NC}"
    echo "Make sure EKS cluster '$CLUSTER_NAME' exists in $AWS_REGION"
    exit 1
fi
echo -e "${GREEN}✓${NC} Connected to cluster"

echo ""
echo "🔒 Step 3: Creating secrets..."

# Check if secrets exist
if ! kubectl get secret postgres-secret -n $NAMESPACE &> /dev/null; then
    echo -e "${YELLOW}⚠️  Secrets not found. Please create secrets manually:${NC}"
    echo ""
    echo "1. Copy secrets template:"
    echo "   cp k8s/secrets.yaml.template k8s/secrets.yaml"
    echo ""
    echo "2. Edit secrets.yaml with real values"
    echo ""
    echo "3. Apply secrets:"
    echo "   kubectl apply -f k8s/secrets.yaml"
    echo ""
    read -p "Press Enter after creating secrets to continue..."
else
    echo -e "${GREEN}✓${NC} Secrets already exist"
fi

echo ""
echo "🚀 Step 4: Deploying to Kubernetes..."

# Update image references in deployment
sed -i.bak "s|image: integmed/backend:latest|image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_PREFIX/backend:latest|g" k8s/deployment.yaml
sed -i.bak "s|image: integmed/frontend:latest|image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_PREFIX/frontend:latest|g" k8s/deployment.yaml

# Apply Kubernetes manifests
kubectl apply -f k8s/deployment.yaml

# Wait for deployments
echo ""
echo "⏳ Waiting for deployments to be ready..."

kubectl wait --for=condition=available --timeout=300s \
    deployment/backend deployment/frontend -n $NAMESPACE || true

echo ""
echo "📊 Deployment status:"
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

echo ""
echo "🔄 Step 5: Running database migrations..."

# Get backend pod name
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=backend -o jsonpath='{.items[0].metadata.name}')

if [ -n "$BACKEND_POD" ]; then
    echo "Running migrations on pod: $BACKEND_POD"
    kubectl exec -n $NAMESPACE $BACKEND_POD -- alembic upgrade head || \
        echo -e "${YELLOW}⚠️  Migration failed. Run manually if needed${NC}"
else
    echo -e "${YELLOW}⚠️  No backend pod found. Skip migrations${NC}"
fi

echo ""
echo "🌐 Step 6: Getting application URL..."

# Wait for load balancer
echo "Waiting for load balancer to be provisioned (this may take 2-3 minutes)..."
sleep 30

INGRESS_HOST=$(kubectl get ingress integmed-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

if [ -z "$INGRESS_HOST" ]; then
    echo -e "${YELLOW}⚠️  Load balancer not ready yet. Check later with:${NC}"
    echo "   kubectl get ingress -n $NAMESPACE"
else
    echo -e "${GREEN}✓${NC} Load Balancer: $INGRESS_HOST"
fi

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access IntegMed:"
if [ -n "$INGRESS_HOST" ]; then
    echo "   URL: https://$INGRESS_HOST"
else
    echo "   Get URL: kubectl get ingress -n $NAMESPACE"
fi
echo ""
echo "🔍 Monitoring:"
echo "   kubectl logs -f deployment/backend -n $NAMESPACE"
echo "   kubectl logs -f deployment/frontend -n $NAMESPACE"
echo "   kubectl get pods -n $NAMESPACE"
echo "   kubectl describe ingress -n $NAMESPACE"
echo ""
echo "🔄 Update deployment:"
echo "   ./deploy-cloud.sh  (rebuild and redeploy)"
echo ""
echo "📊 Scaling:"
echo "   kubectl scale deployment/backend --replicas=5 -n $NAMESPACE"
echo ""
echo "🛑 Delete deployment:"
echo "   kubectl delete namespace $NAMESPACE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "   1. Update DNS to point to load balancer"
echo "   2. Update SSL certificate ARN in k8s/deployment.yaml"
echo "   3. Configure monitoring and alerts"
echo "   4. Set up CI/CD pipeline"
echo ""
