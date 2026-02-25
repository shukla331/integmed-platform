# IntegMed - Complete Deployment Guide

## 🎯 **Quick Start Options**

### Option 1: Local Development (5 minutes)
```bash
cd integmed-deployment
chmod +x deploy-local.sh
./deploy-local.sh
```
✅ **Done!** Visit http://localhost:3000

### Option 2: AWS Cloud Production (30 minutes)
```bash
cd integmed-deployment
chmod +x deploy-cloud.sh
./deploy-cloud.sh
```
✅ **Done!** Your app is live on AWS!

---

## 📦 **What's Included**

This deployment package contains:

### ✅ Frontend (Next.js 14)
- 🔐 HPR authentication with OTP
- 📝 Prescription page with shorthand expansion
- 💊 Drug interaction checking (real-time)
- 👥 Patient dashboard
- 📱 Fully responsive design
- ⚡ API integration complete

### ✅ Backend (FastAPI + PostgreSQL)
- All migrations ready
- API endpoints functional
- Database schema complete
- Docker-ready

### ✅ Deployment Infrastructure
- 🐳 Docker Compose for local dev
- ☸️ Kubernetes for production
- 🌐 Nginx reverse proxy
- 🔒 SSL/TLS configuration
- 📈 Auto-scaling setup
- 💾 Database persistence

---

## 🚀 **Deployment Methods**

### **Method 1: Docker Compose (Local Development)**

**Prerequisites:**
- Docker Desktop installed
- 4GB RAM minimum

**Steps:**
```bash
# 1. Extract all files
tar -xzf integmed-backend.tar.gz
unzip integmed-frontend.zip

# 2. Run deployment
cd integmed-deployment
./deploy-local.sh

# 3. Access application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000/api/docs
```

**Management:**
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build
```

---

### **Method 2: AWS EKS (Production)**

**Prerequisites:**
- AWS account with admin access
- AWS CLI configured (`aws configure`)
- kubectl installed
- Docker installed
- Budget: ~₹50,000/month for small scale

**Infrastructure Setup (One-time):**

```bash
# 1. Create EKS cluster (using eksctl - easiest)
eksctl create cluster \
  --name integmed-prod \
  --region ap-south-1 \
  --nodegroup-name standard-workers \
  --node-type t3.xlarge \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 10 \
  --managed

# This takes 15-20 minutes

# 2. Install AWS Load Balancer Controller
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"

helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=integmed-prod

# 3. Create RDS PostgreSQL (managed database)
# Use AWS Console or Terraform:
# - Engine: PostgreSQL 16
# - Instance: db.r6g.xlarge
# - Storage: 100GB
# - Multi-AZ: Yes
# - Region: ap-south-1 (Mumbai)
```

**Application Deployment:**

```bash
# 1. Clone deployment repo
cd integmed-deployment

# 2. Update secrets
cp k8s/secrets.yaml.template k8s/secrets.yaml
nano k8s/secrets.yaml  # Add real passwords

# 3. Deploy
./deploy-cloud.sh

# 4. Monitor deployment
kubectl get pods -n integmed-prod
kubectl logs -f deployment/backend -n integmed-prod
```

**Post-Deployment:**

```bash
# Get load balancer URL
kubectl get ingress -n integmed-prod

# Example output:
# integmed-ingress ... abc123-456.ap-south-1.elb.amazonaws.com

# 1. Update DNS (Route 53 or your provider)
#    integmed.health → abc123-456.ap-south-1.elb.amazonaws.com

# 2. Get SSL certificate (AWS Certificate Manager - FREE)
#    - Request certificate for integmed.health
#    - Add DNS validation records
#    - Update ingress annotation with certificate ARN

# 3. Update k8s/deployment.yaml with certificate:
#    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:ap-south-1:ACCOUNT:certificate/ID
```

---

### **Method 3: Azure AKS (Alternative Cloud)**

Similar to AWS but uses Azure services:

```bash
# Create AKS cluster
az aks create \
  --resource-group integmed-rg \
  --name integmed-prod \
  --location centralindia \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3

# Get credentials
az aks get-credentials --resource-group integmed-rg --name integmed-prod

# Deploy (use same Kubernetes manifests)
kubectl apply -f k8s/
```

---

## 🔧 **Configuration**

### Environment Variables

**Backend (.env):**
```bash
DATABASE_URL=postgresql://user:pass@postgres:5432/integmed
REDIS_URL=redis://redis:6379/0
SECRET_KEY=generate-with-openssl-rand-hex-32
ENVIRONMENT=production
DEBUG=False

# ABDM Credentials (get from sandbox.abdm.gov.in)
ABDM_GATEWAY_URL=https://abdm.gov.in/gateway
ABDM_CLIENT_ID=your-client-id
ABDM_CLIENT_SECRET=your-secret

# HPR API
HPR_API_URL=https://hprid.abdm.gov.in/api
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=https://integmed.health  # or http://localhost:8000
```

### Secrets Management

**For Production:**
```bash
# Option 1: AWS Secrets Manager (Recommended)
aws secretsmanager create-secret \
  --name integmed/database \
  --secret-string '{"username":"integmed","password":"strong-pass"}'

# Option 2: Kubernetes Secrets (Basic)
kubectl create secret generic postgres-secret \
  --from-literal=username=integmed \
  --from-literal=password=strong-password \
  -n integmed-prod
```

---

## 📊 **Monitoring & Logs**

### Local Development
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Real-time container stats
docker stats
```

### Production (Kubernetes)
```bash
# Pod logs
kubectl logs -f deployment/backend -n integmed-prod

# Multiple pods
kubectl logs -f -l app=backend -n integmed-prod

# Pod status
kubectl get pods -n integmed-prod -w

# Resource usage
kubectl top pods -n integmed-prod
```

### Set Up Monitoring (Recommended)

```bash
# Install Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Login: admin / prom-operator
# Import dashboard ID: 315 (Kubernetes cluster monitoring)
```

---

## 🔒 **Security Checklist**

### Before Going Live:

- [ ] **Change all default passwords**
  ```bash
  # Generate strong passwords
  openssl rand -base64 32
  ```

- [ ] **Enable SSL/TLS**
  - Get certificate from Let's Encrypt (free) or AWS ACM
  - Update Nginx/Ingress config

- [ ] **Set up firewall rules**
  - Only port 443 (HTTPS) public
  - Port 8000 (API) only from frontend
  - PostgreSQL only from backend
  - No SSH from public internet

- [ ] **Enable database encryption**
  - RDS: Enable encryption at rest
  - PostgreSQL: Enable SSL connections

- [ ] **Set up backups**
  ```bash
  # Automated PostgreSQL backups
  kubectl create cronjob db-backup \
    --image=postgres:16 \
    --schedule="0 2 * * *" \
    -- pg_dump -h postgres -U integmed integmed > backup.sql
  ```

- [ ] **Implement rate limiting** (already in Nginx config)

- [ ] **Add WAF (Web Application Firewall)**
  - AWS: Enable AWS WAF on ALB
  - Azure: Enable Azure Front Door

- [ ] **Scan for vulnerabilities**
  ```bash
  # Scan Docker images
  docker scan integmed/backend:latest
  ```

---

## 💰 **Cost Estimation**

### AWS Cloud (Mumbai Region)

**Small Scale (100-500 users):**
- EKS Cluster: ₹5,000/month
- EC2 (3x t3.xlarge): ₹25,000/month
- RDS PostgreSQL: ₹15,000/month
- Load Balancer: ₹2,000/month
- Data Transfer: ₹3,000/month
- **Total: ~₹50,000/month** (~$600)

**Medium Scale (500-2000 users):**
- EKS Cluster: ₹5,000/month
- EC2 (5x t3.2xlarge): ₹60,000/month
- RDS PostgreSQL: ₹30,000/month
- Load Balancer: ₹3,000/month
- Data Transfer: ₹10,000/month
- **Total: ~₹1,08,000/month** (~$1,300)

**Cost Optimization Tips:**
- Use Reserved Instances (40% savings)
- Use Spot Instances for non-critical workloads
- Enable auto-scaling (scale down at night)
- Use CloudFront CDN for frontend
- Compress images and enable caching

---

## 🐛 **Troubleshooting**

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready
docker-compose exec postgres pg_isready

# 2. Migration errors
docker-compose exec backend alembic current

# 3. Port already in use
lsof -ti:8000 | xargs kill -9
```

### Frontend Won't Build

```bash
# Check Node version (need 18+)
node --version

# Clear cache
rm -rf frontend/.next frontend/node_modules
cd frontend && npm install
```

### Database Connection Failed

```bash
# Test connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine.connect())"

# Check PostgreSQL
docker-compose exec postgres psql -U integmed -d integmed -c "SELECT 1"
```

### Kubernetes Pods Crashing

```bash
# Describe pod
kubectl describe pod POD_NAME -n integmed-prod

# Check events
kubectl get events -n integmed-prod --sort-by='.lastTimestamp'

# Check resource limits
kubectl top pods -n integmed-prod
```

---

## 🔄 **CI/CD Pipeline (GitHub Actions)**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-south-1
      
      - name: Build and Push
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}
          docker build -t integmed/backend backend/
          docker push ${{ secrets.ECR_REGISTRY }}/integmed/backend:latest
      
      - name: Deploy to EKS
        run: |
          aws eks update-kubeconfig --name integmed-prod --region ap-south-1
          kubectl rollout restart deployment/backend -n integmed-prod
```

---

## 📞 **Support**

### Getting Help:

1. **Check logs first** (90% of issues are in logs)
2. **Search GitHub Issues** for similar problems
3. **Contact team** via Slack/Email

### Useful Commands Reference:

```bash
# Quick health check
curl http://localhost:8000/health

# Database shell
docker-compose exec postgres psql -U integmed

# Backend shell
docker-compose exec backend python

# Restart everything
docker-compose restart

# Clean slate
docker-compose down -v  # ⚠️ Deletes data!
./deploy-local.sh
```

---

## ✅ **Pre-Launch Checklist**

- [ ] All tests passing
- [ ] Security audit completed
- [ ] SSL certificate installed
- [ ] Database backups configured
- [ ] Monitoring/alerting set up
- [ ] DNS configured
- [ ] ABDM sandbox testing complete
- [ ] Legal documents ready (T&C, Privacy Policy)
- [ ] Support system ready (helpdesk/ticketing)
- [ ] Documentation complete
- [ ] Team trained
- [ ] Disaster recovery plan tested

---

**Ready to launch? Let's go! 🚀**

For questions: engineering@integmed.health
