## `README.md`

Below is a complete README for your current **RideX** architecture, including the passenger app, driver app, admin dashboard, API Gateway, microservices, PostgreSQL, Docker, Kubernetes, and tests.

````markdown
# RideX

> AI-ready ride-hailing and mobility platform built with microservices, FastAPI, React, PostgreSQL, Docker, and Kubernetes.

---

## 1. Overview

RideX is a scalable ride-hailing platform designed around a microservices architecture.

The platform supports:

- Passenger registration and login
- Driver registration and login
- Driver online/offline status
- Ride booking
- Driver matching
- Ride acceptance
- Navigation
- Fare calculation
- Surge pricing
- Payments
- Notifications
- Ratings
- SOS / safety
- Driver earnings
- Admin dashboard
- Reports and analytics

---

## 2. Architecture

```text
                         ┌──────────────────────┐
                         │     Passenger App    │
                         │      React / Web     │
                         └──────────┬───────────┘
                                    │
                                    │
                         ┌──────────▼───────────┐
                         │     Driver App       │
                         │      React / Web     │
                         └──────────┬───────────┘
                                    │
                                    │
                         ┌──────────▼───────────┐
                         │   Admin Dashboard    │
                         │      React / Web     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     API Gateway      │
                         │     FastAPI :8000    │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
      │ User Service│       │Driver Service│      │ Ride Service │
      │    :8001    │       │    :8002     │      │    :8003     │
      └─────────────┘       └─────────────┘       └──────┬──────┘
                                                          │
                  ┌───────────────────────────────────────┤
                  │                                       │
                  ▼                                       ▼
          ┌───────────────┐                       ┌───────────────┐
          │   Matching    │                       │   Pricing     │
          │   Service     │                       │   Service     │
          │    :8004      │                       │    :8005      │
          └───────────────┘                       └───────────────┘

                  ┌───────────────────────────────────────┐
                  │                                       │
                  ▼                                       ▼
          ┌───────────────┐                       ┌───────────────┐
          │   Payment     │                       │ Notification  │
          │   Service     │                       │   Service     │
          │    :8006      │                       │    :8007      │
          └───────────────┘                       └───────────────┘

                                  │
                                  ▼
                         ┌──────────────────────┐
                         │ Rating / Safety     │
                         │      :8008          │
                         └──────────────────────┘

                                  │
                                  ▼
                         ┌──────────────────────┐
                         │     PostgreSQL       │
                         │       :5432          │
                         └──────────────────────┘
````

---

# 3. Technology Stack

## Frontend

* React
* JavaScript
* HTML
* CSS
* REST APIs

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy

## Database

* PostgreSQL

## Infrastructure

* Docker
* Docker Compose
* Kubernetes
* Minikube

## Testing

* Pytest
* FastAPI TestClient
* HTTPX

## Future / AI

RideX can be extended with:

* AI driver matching
* AI demand prediction
* AI surge prediction
* ETA prediction
* Fraud detection
* Driver behavior analysis
* Customer support AI agent
* Voice assistant
* AI operations assistant
* Predictive maintenance
* Intelligent dispatch

---

# 4. Project Structure

```text
RideX/
│
├── README.md
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
│
├── api-gateway/
│   ├── main.py
│   ├── routes.py
│   └── config.py
│
├── passenger-app/
│   ├── package.json
│   └── src/
│
├── driver-app/
│   ├── package.json
│   └── src/
│       ├── login/
│       │   └── login.js
│       ├── online-offline/
│       │   └── driver_status.js
│       ├── ride-request/
│       │   └── ride_request.js
│       ├── accept-ride/
│       │   └── accept_ride.js
│       ├── navigation/
│       │   └── navigation.js
│       └── earnings/
│           └── earnings.js
│
├── admin-dashboard/
│   ├── package.json
│   └── src/
│       ├── users/
│       │   └── users.js
│       ├── drivers/
│       │   └── drivers.js
│       ├── rides/
│       │   └── rides.js
│       ├── payments/
│       │   └── payments.js
│       └── reports/
│           └── reports.js
│
├── services/
│   │
│   ├── user_service/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── database.py
│   │
│   ├── driver_service/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── database.py
│   │
│   ├── ride_service/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── database.py
│   │
│   ├── matching_service/
│   │   ├── main.py
│   │   ├── matching_engine.py
│   │   ├── driver_search.py
│   │   └── distance.py
│   │
│   ├── pricing_service/
│   │   ├── main.py
│   │   ├── fare_engine.py
│   │   ├── surge.py
│   │   └── pricing_rules.py
│   │
│   ├── payment_service/
│   │   ├── main.py
│   │   ├── payment.py
│   │   └── gateway.py
│   │
│   ├── notification_service/
│   │   ├── main.py
│   │   ├── push_notification.py
│   │   ├── sms.py
│   │   └── email.py
│   │
│   └── rating_safety_service/
│       ├── main.py
│       ├── rating.py
│       ├── safety.py
│       └── sos.py
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── infrastructure/
│   │
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   │
│   └── kubernetes/
│       ├── namespace.yaml
│       ├── api-gateway.yaml
│       ├── user-service.yaml
│       ├── driver-service.yaml
│       ├── ride-service.yaml
│       ├── matching-service.yaml
│       ├── pricing-service.yaml
│       ├── payment-service.yaml
│       ├── notification-service.yaml
│       └── rating-safety-service.yaml
│
└── tests/
    ├── test_users.py
    ├── test_drivers.py
    ├── test_rides.py
    ├── test_matching.py
    └── test_pricing.py
```

---

# 5. Service Ports

| Service               | Port |
| --------------------- | ---: |
| API Gateway           | 8000 |
| User Service          | 8001 |
| Driver Service        | 8002 |
| Ride Service          | 8003 |
| Matching Service      | 8004 |
| Pricing Service       | 8005 |
| Payment Service       | 8006 |
| Notification Service  | 8007 |
| Rating/Safety Service | 8008 |
| PostgreSQL            | 5432 |
| Redis                 | 6379 |

---

# 6. Prerequisites

Install:

* Python 3.11+
* Node.js 20+
* npm
* Git
* Docker
* Docker Compose
* kubectl
* Minikube

Check versions:

```bash
python3 --version
node --version
npm --version
git --version
docker --version
kubectl version --client
minikube version
```

---

# 7. Clone Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd RideX
```

---

# 8. Python Virtual Environment

Create virtual environment:

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 9. Environment Configuration

Create `.env`:

```bash
cp .env.example .env
```

Edit:

```bash
nano .env
```

Example:

```env
APP_NAME=RideX
APP_ENV=development
DEBUG=true

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ridex
POSTGRES_USER=ridex
POSTGRES_PASSWORD=CHANGE_ME

DATABASE_URL=postgresql://ridex:CHANGE_ME@postgres:5432/ridex

JWT_SECRET_KEY=CHANGE_ME
JWT_ALGORITHM=HS256

SEARCH_RADIUS_KM=5
MAX_DRIVER_RESULTS=10
MATCH_TIMEOUT_SECONDS=30

BASE_FARE=50
PER_KM_RATE=15
PER_MINUTE_RATE=2
MINIMUM_FARE=50
MAX_SURGE_MULTIPLIER=3.0
```

Never commit `.env`.

---

# 10. Run PostgreSQL

Using Docker Compose:

```bash
docker compose \
  -f infrastructure/docker/docker-compose.yml \
  up -d postgres
```

Check:

```bash
docker ps
```

---

# 11. Initialize Database

Run the schema:

```bash
psql \
  -h localhost \
  -U ridex \
  -d ridex \
  -f database/schema.sql
```

Load test data:

```bash
psql \
  -h localhost \
  -U ridex \
  -d ridex \
  -f database/seed.sql
```

---

# 12. Run API Gateway

From the project root:

```bash
uvicorn api-gateway.main:app --host 0.0.0.0 --port 8000
```

If the directory is named `api_gateway` instead of `api-gateway`:

```bash
uvicorn api_gateway.main:app --host 0.0.0.0 --port 8000
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 13. Run Individual Services

## User Service

```bash
uvicorn services.user_service.main:app \
  --host 0.0.0.0 \
  --port 8001
```

## Driver Service

```bash
uvicorn services.driver_service.main:app \
  --host 0.0.0.0 \
  --port 8002
```

## Ride Service

```bash
uvicorn services.ride_service.main:app \
  --host 0.0.0.0 \
  --port 8003
```

## Matching Service

```bash
uvicorn services.matching_service.main:app \
  --host 0.0.0.0 \
  --port 8004
```

## Pricing Service

```bash
uvicorn services.pricing_service.main:app \
  --host 0.0.0.0 \
  --port 8005
```

## Payment Service

```bash
uvicorn services.payment_service.main:app \
  --host 0.0.0.0 \
  --port 8006
```

## Notification Service

```bash
uvicorn services.notification_service.main:app \
  --host 0.0.0.0 \
  --port 8007
```

## Rating/Safety Service

```bash
uvicorn services.rating_safety_service.main:app \
  --host 0.0.0.0 \
  --port 8008
```

---

# 14. API Health Checks

Test API Gateway:

```bash
curl http://localhost:8000/health
```

User Service:

```bash
curl http://localhost:8001/health
```

Driver Service:

```bash
curl http://localhost:8002/health
```

Ride Service:

```bash
curl http://localhost:8003/health
```

Matching Service:

```bash
curl http://localhost:8004/health
```

Pricing Service:

```bash
curl http://localhost:8005/health
```

---

# 15. Run Frontend Applications

## Driver App

```bash
cd driver-app
npm install
npm start
```

## Admin Dashboard

```bash
cd admin-dashboard
npm install
npm start
```

## Passenger App

```bash
cd passenger-app
npm install
npm start
```

---

# 16. Run Tests

Run all tests:

```bash
pytest -v
```

Run user tests:

```bash
pytest tests/test_users.py -v
```

Run driver tests:

```bash
pytest tests/test_drivers.py -v
```

Run ride tests:

```bash
pytest tests/test_rides.py -v
```

Run matching tests:

```bash
pytest tests/test_matching.py -v
```

Run pricing tests:

```bash
pytest tests/test_pricing.py -v
```

---

# 17. Docker Build

Build the RideX Docker image:

```bash
docker build \
  -f infrastructure/docker/Dockerfile \
  -t ridex:latest \
  .
```

Check:

```bash
docker images
```

---

# 18. Docker Compose

Start all containers:

```bash
docker compose \
  -f infrastructure/docker/docker-compose.yml \
  up -d
```

Check:

```bash
docker compose \
  -f infrastructure/docker/docker-compose.yml \
  ps
```

View logs:

```bash
docker compose \
  -f infrastructure/docker/docker-compose.yml \
  logs -f
```

Stop:

```bash
docker compose \
  -f infrastructure/docker/docker-compose.yml \
  down
```

---

# 19. Kubernetes

RideX can run on Kubernetes using Minikube.

Start Minikube:

```bash
minikube start
```

Verify:

```bash
kubectl get nodes
```

Expected:

```text
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   ...   ...
```

---

# 20. Kubernetes Namespace

Create the namespace:

```bash
kubectl apply \
  -f infrastructure/kubernetes/namespace.yaml
```

Verify:

```bash
kubectl get namespaces
```

Check RideX:

```bash
kubectl get all -n ridex
```

---

# 21. Build Images for Minikube

Configure Docker to use Minikube's Docker daemon:

```bash
eval $(minikube docker-env)
```

Build the services:

```bash
docker build \
  -t ridex-user-service:latest \
  -f infrastructure/docker/Dockerfile \
  .
```

Repeat for the required service images.

Verify:

```bash
docker images | grep ridex
```

---

# 22. Deploy Kubernetes Services

API Gateway:

```bash
kubectl apply \
  -f infrastructure/kubernetes/api-gateway.yaml
```

User Service:

```bash
kubectl apply \
  -f infrastructure/kubernetes/user-service.yaml
```

Driver Service:

```bash
kubectl apply \
  -f infrastructure/kubernetes/driver-service.yaml
```

Ride Service:

```bash
kubectl apply \
  -f infrastructure/kubernetes/ride-service.yaml
```

Matching Service:

```bash
kubectl apply \
  -f infrastructure/kubernetes/matching-service.yaml
```

Pricing Service:

```bash
kubectl apply \
  -f infrastructure/kubernetes/pricing-service.yaml
```

Payment Service:

```bash
kubectl apply \
  -f infrastructure/kubernetes/payment-service.yaml
```

Notification Service:

```bash
kubectl apply \
  -f infrastructure/kubernetes/notification-service.yaml
```

Rating/Safety:

```bash
kubectl apply \
  -f infrastructure/kubernetes/rating-safety-service.yaml
```

---

# 23. Check Kubernetes

Pods:

```bash
kubectl get pods -n ridex
```

Services:

```bash
kubectl get svc -n ridex
```

Deployments:

```bash
kubectl get deployments -n ridex
```

All resources:

```bash
kubectl get all -n ridex
```

---

# 24. Debug Kubernetes

If a pod is not running:

```bash
kubectl get pods -n ridex
```

Then:

```bash
kubectl describe pod <POD_NAME> -n ridex
```

View logs:

```bash
kubectl logs <POD_NAME> -n ridex
```

Follow logs:

```bash
kubectl logs -f <POD_NAME> -n ridex
```

---

# 25. Kubernetes API Gateway

Get the API Gateway service:

```bash
kubectl get svc api-gateway -n ridex
```

For Minikube:

```bash
minikube service api-gateway -n ridex
```

---

# 26. Ride Lifecycle

The basic RideX ride lifecycle is:

```text
Passenger
   │
   │ Request Ride
   ▼
REQUESTED
   │
   ▼
SEARCHING
   │
   ▼
DRIVER_ASSIGNED
   │
   ▼
DRIVER_ARRIVING
   │
   ▼
STARTED
   │
   ▼
COMPLETED
```

Cancellation:

```text
REQUESTED
    │
SEARCHING
    │
DRIVER_ASSIGNED
    │
DRIVER_ARRIVING
    │
    └──────────────► CANCELLED
```

---

# 27. Driver Lifecycle

```text
OFFLINE
   │
   ▼
ONLINE
   │
   ▼
AVAILABLE
   │
   ▼
RIDE_REQUESTED
   │
   ▼
RIDE_ACCEPTED
   │
   ▼
ON_TRIP
   │
   ▼
AVAILABLE
```

---

# 28. Matching Algorithm

The Matching Service performs:

```text
Ride Request
     │
     ▼
Get Available Drivers
     │
     ▼
Filter Vehicle Type
     │
     ▼
Calculate Distance
     │
     ▼
Calculate ETA
     │
     ▼
Rank Drivers
     │
     ▼
Select Best Candidate
     │
     ▼
Send Ride Request
```

Primary matching factors:

* Distance
* Driver availability
* Vehicle type
* Driver rating
* Estimated arrival time
* Driver acceptance behavior
* Current driver workload

---

# 29. Pricing Algorithm

Ride fare can be calculated using:

```text
Fare =
Base Fare
+ Distance Charge
+ Time Charge
+ Surge Charge
+ Additional Fees
- Discounts
```

Example:

```text
Base Fare       = ₹50
Distance        = 10 km
Per KM          = ₹15
Time            = 20 min
Per Minute      = ₹2

Distance Charge = 10 × ₹15 = ₹150
Time Charge     = 20 × ₹2  = ₹40

Subtotal        = ₹50 + ₹150 + ₹40
                = ₹240
```

If surge is `1.5x`:

```text
Final Fare = ₹240 × 1.5

Final Fare = ₹360
```

---

# 30. Payment Flow

```text
Ride Completed
      │
      ▼
Calculate Final Fare
      │
      ▼
Payment Service
      │
      ├── Payment Gateway
      │
      ├── Payment Validation
      │
      └── Transaction Record
      │
      ▼
Payment Successful
      │
      ▼
Notification
      │
      ▼
Receipt
```

Development mode uses:

```env
PAYMENT_PROVIDER=mock
```

Production should use a real payment provider.

---

# 31. Notification Flow

RideX supports:

```text
Push Notification
SMS
Email
```

Examples:

```text
Ride Requested
Driver Found
Driver Arriving
Ride Started
Ride Completed
Payment Successful
Ride Cancelled
SOS Activated
```

---

# 32. Safety

The Rating/Safety Service handles:

* Passenger ratings
* Driver ratings
* Ride feedback
* SOS
* Safety events
* Emergency notifications
* Incident records

SOS flow:

```text
Passenger / Driver
       │
       ▼
     SOS
       │
       ▼
Safety Service
       │
       ├── Record Incident
       ├── Notify Emergency Contacts
       ├── Notify Platform
       └── Track Ride
```

---

# 33. Security

Never commit:

```text
.env
passwords
API keys
JWT secrets
private keys
certificates
payment credentials
```

Use:

```text
.env
Kubernetes Secrets
Cloud Secret Manager
AWS Secrets Manager
Azure Key Vault
Google Secret Manager
```

for sensitive information.

---

# 34. Production Architecture

The future production architecture can use:

```text
                         Internet
                            │
                            ▼
                       Load Balancer
                            │
                            ▼
                       API Gateway
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
      User              Driver               Ride
     Service            Service             Service
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
             ┌──────────────┼───────────────┐
             │              │               │
             ▼              ▼               ▼
         Matching        Pricing         Payment
          Service        Service          Service
             │              │               │
             └──────────────┼───────────────┘
                            │
                    Event / Message Bus
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        Notification      Rating          Safety
          Service         Service         Service
                            │
                            ▼
                       PostgreSQL
                            │
                            ▼
                           Redis
```

---

# 35. Future AI Architecture

RideX can evolve into an AI-enabled mobility platform.

```text
                    RideX Platform
                          │
                          ▼
                    AI Orchestrator
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
   AI Matching       AI Pricing         AI Support
      Agent             Agent              Agent
        │                 │                  │
        ▼                 ▼                  ▼
 Driver ETA          Demand Forecast     Customer Chat
 Prediction          Surge Prediction    Voice Assistant
        │                 │
        └─────────────────┼─────────────────┘
                          ▼
                    AI Telemetry
                          │
                          ▼
                  Monitoring / Evaluation
```

Potential AI capabilities:

* Intelligent driver matching
* Demand forecasting
* Dynamic pricing
* ETA prediction
* Fraud detection
* Driver churn prediction
* Customer support agent
* Voice-based ride booking
* Safety anomaly detection
* Fleet optimization
* Predictive maintenance

---

# 36. Development Workflow

Recommended workflow:

```text
1. Develop
      ↓
2. Unit Test
      ↓
3. Build Docker Image
      ↓
4. Run Docker Compose
      ↓
5. Integration Test
      ↓
6. Deploy to Minikube
      ↓
7. Kubernetes Test
      ↓
8. CI/CD
      ↓
9. Cloud Deployment
```

---

# 37. Git Workflow

Check status:

```bash
git status
```

Add files:

```bash
git add .
```

Commit:

```bash
git commit -m "Initial RideX microservices platform"
```

Push:

```bash
git push origin main
```

Before committing:

```bash
git status
```

Make sure `.env` is not included.

---

# 38. Common Kubernetes Error

If you see:

```text
The connection to the server localhost:8080 was refused
```

check:

```bash
kubectl config current-context
```

Then:

```bash
kubectl cluster-info
```

For Minikube:

```bash
minikube status
```

Start it if necessary:

```bash
minikube start
```

Then:

```bash
kubectl get nodes
```

Expected:

```text
minikube   Ready
```

---

# 39. Common Docker Error

If Docker is not installed:

```bash
docker --version
```

If Docker is unavailable, install/configure Docker before running:

```bash
docker compose up
```

On systems where Podman is installed, check:

```bash
rpm -qa | grep podman
```

If `podman-docker` conflicts with Docker CE, resolve the package conflict before installing Docker CE.

---

# 40. Troubleshooting

### Pods not starting

```bash
kubectl get pods -n ridex
```

```bash
kubectl describe pod <POD_NAME> -n ridex
```

```bash
kubectl logs <POD_NAME> -n ridex
```

### Service unavailable

```bash
kubectl get svc -n ridex
```

Check endpoints:

```bash
kubectl get endpoints -n ridex
```

### ImagePullBackOff

If using Minikube:

```bash
eval $(minikube docker-env)
```

Build the image again:

```bash
docker build -t <IMAGE_NAME>:latest .
```

Then:

```bash
kubectl rollout restart deployment <DEPLOYMENT_NAME> -n ridex
```

---

# 41. Current Service Map

```text
API Gateway
     │
     ├── User Service
     │
     ├── Driver Service
     │
     ├── Ride Service
     │
     ├── Matching Service
     │
     ├── Pricing Service
     │
     ├── Payment Service
     │
     ├── Notification Service
     │
     └── Rating/Safety Service
```

---

# 42. Testing Strategy

RideX uses multiple testing levels:

```text
                    Testing
                       │
        ┌──────────────┼───────────────┐
        │              │               │
        ▼              ▼               ▼
     Unit Tests    API Tests      Integration Tests
        │              │               │
        ▼              ▼               ▼
     Pytest       TestClient       PostgreSQL
                                   Docker/K8s
```

Future tests:

* Authentication tests
* Driver availability tests
* Matching accuracy tests
* Pricing tests
* Payment tests
* Notification tests
* SOS tests
* End-to-end ride tests
* Load tests
* Security tests

---

# 43. License

This project is currently for development and educational purposes.

Add your production license here before public distribution.

---

# 44. Roadmap

## Phase 1 - Foundation

* [x] Project structure
* [x] User service
* [x] Driver service
* [x] Ride service
* [x] Matching service
* [x] Pricing service
* [x] Payment service
* [x] Notification service
* [x] Rating/Safety service

## Phase 2 - Infrastructure

* [x] Docker
* [x] Docker Compose
* [x] Kubernetes manifests
* [ ] Kubernetes ConfigMap
* [ ] Kubernetes Secrets
* [ ] PostgreSQL StatefulSet
* [ ] Redis
* [ ] Ingress
* [ ] Persistent Volumes

## Phase 3 - Applications

* [ ] Passenger application
* [x] Driver application structure
* [x] Admin dashboard structure
* [ ] Authentication UI
* [ ] Live maps
* [ ] Real-time driver tracking

## Phase 4 - Production

* [ ] CI/CD
* [ ] Monitoring
* [ ] Logging
* [ ] Distributed tracing
* [ ] API security
* [ ] Rate limiting
* [ ] Autoscaling
* [ ] Backup and disaster recovery

## Phase 5 - AI

* [ ] AI driver matching
* [ ] AI demand forecasting
* [ ] AI surge prediction
* [ ] ETA prediction
* [ ] Fraud detection
* [ ] AI customer support
* [ ] Voice assistant
* [ ] AI operations assistant
* [ ] AI observability

---

# 45. Quick Start

For a quick local development environment:

```bash
git clone <YOUR_REPOSITORY_URL>

cd RideX

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

docker compose \
  -f infrastructure/docker/docker-compose.yml \
  up -d

pytest -v
```

Then start the API:

```bash
uvicorn api_gateway.main:app \
  --host 0.0.0.0 \
  --port 8000
```

Open:

```text
http://localhost:8000/docs
```

---

# 46. Project Status

RideX is currently under active development.

The architecture is designed to evolve from:

```text
Local Development
       ↓
Docker Compose
       ↓
Minikube
       ↓
Kubernetes
       ↓
Cloud Kubernetes
       ↓
AI-enabled Ride Platform
```

---

## RideX

**Ride. Match. Move.**

```text
Passenger → Ride → Matching → Driver → Trip → Payment → Rating
```

```
```

