# 🚀 Project 05 – Containerized URL Shortener Platform with CI/CD, Self-Hosted Runner, Watchtower & Discord Notifications

## Overview

This project demonstrates a production-style containerized platform built with Docker, Docker Compose, GitHub Actions, Docker Hub, a self-hosted runner, Watchtower, and Discord notifications.

The goal of this project is to simulate how modern applications are built, tested, packaged, deployed, and automatically updated without manually SSH'ing into servers.

---

# Architecture

```
Developer
    │
    ▼
Git Push
    │
    ▼
GitHub Actions CI
(Pytest + Ruff + Docker Build)
    │
    ▼
Docker Hub
(new image)
    │
    ▼
Docker Compose Stack
────────────────────────
Nginx
Flask + Gunicorn
Redis
PostgreSQL
Watchtower
────────────────────────
    │
    ▼
Watchtower polls Docker Hub
every 30 seconds
    │
    ▼
New image detected
    │
    ▼
Old url-app container stopped
    │
    ▼
New url-app container started
    │
    ▼
Discord Notification
```

---

# Technologies Used

* Python Flask
* Gunicorn
* Nginx
* Redis
* PostgreSQL
* Docker
* Docker Compose
* GitHub Actions
* Docker Hub
* Self-hosted Runner
* Watchtower
* Discord Webhooks

---

# Project Structure

```
project-5-url-shortener/

├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
│
├── tests/
│   └── test_app.py
│
├── nginx/
│   └── default.conf
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── docker-compose.yml
├── .env
├── .dockerignore
└── README.md
```

---

# Application Components

## Flask

Provides the URL shortener API.

---

## Gunicorn

Production WSGI server.

Port:

```
8000
```

---

## Nginx

Reverse proxy.

Receives traffic on:

```
80
```

Forwards requests to:

```
url-app:8000
```

---

## Redis

Used as cache layer.

---

## PostgreSQL

Persistent database.

Uses named volume:

```
postgres-data
```

so container deletion does not destroy data.

---

# Dockerfile Flow

Dockerfile is responsible for creating the image.

CI only cares about:

```
app.py
requirements.txt
Dockerfile
```

Flow:

```
Code
↓
Dockerfile
↓
Build Image
↓
Push Image to Docker Hub
```

The Dockerfile:

* Installs dependencies
* Creates non-root user
* Copies application files
* Runs Gunicorn

Container listens on:

```
8000
```

---

# Docker Compose

Docker Compose is responsible for running the stack.

It creates:

```
url-app
nginx
redis
postgres
watchtower
```

Compose also creates:

* network
* volumes

Compose does NOT build images anymore.

Instead:

```
url-app:
image: syedaftab04/project05-url-shortener:latest
```

so Docker Hub becomes the source of truth.

---

# CI Pipeline

CI means Continuous Integration.

Purpose:

* Run tests
* Run Ruff
* Build image
* Push image

Flow:

```
git push
↓
GitHub Actions
↓
Pytest
↓
Ruff
↓
Docker Build
↓
Docker Hub
```

CI reads:

```
Dockerfile
```

NOT docker-compose.yml

---

# Docker Hub

Docker Hub stores images.

Tag:

```
syedaftab04/project05-url-shortener:latest
```

Each push creates a new image digest.

Example:

Old:

```
sha256:1111
```

New:

```
sha256:2222
```

Watchtower compares these digests.

---

# CD Workflow

CD means Continuous Deployment.

Purpose:

Bring containers online.

Runs on:

Self-hosted runner

Commands:

```
docker compose pull
docker compose up -d
```

CD creates:

```
nginx
url-app
redis
postgres
watchtower
```

CD is useful when:

* new server created
* server rebuilt
* stack destroyed

---

# Self-Hosted Runner

Runner runs inside WSL.

GitHub sends jobs to runner.

```
GitHub
↓
Runner
↓
Docker Compose
```

No SSH required.

---

# Watchtower

Watchtower replaces manual deployments.

Watchtower polls every:

```
30 seconds
```

It checks:

```
syedaftab04/project05-url-shortener:latest
```

When digest changes:

```
docker pull
↓
stop old url-app
↓
remove old url-app
↓
start new url-app
```

Only url-app is updated.

Redis, PostgreSQL and Nginx remain untouched.

---

# Why Only url-app Updates

Because url-app has label:

```
com.centurylinklabs.watchtower.enable=true
```

Watchtower ignores:

* redis
* postgres
* nginx

---

# Watchtower Docker Socket

Watchtower mounts:

```
/var/run/docker.sock
```

This allows Watchtower to talk directly to Docker Engine.

Watchtower never runs:

```
docker compose up
```

Instead it talks directly to Docker API.

---

# Discord Notifications

Watchtower sends notifications after updates.

Flow:

```
New image
↓
Pull image
↓
Replace container
↓
Discord message
```

---

# CI vs CD vs Watchtower

## CI

Builds image.

```
Code
↓
Dockerfile
↓
Docker Hub
```

---

## CD

Creates stack.

```
Docker Hub
↓
docker compose up
↓
Containers online
```

---

## Watchtower

Updates running containers.

```
Docker Hub
↓
New digest
↓
Replace url-app
```

---

# First Deployment

```
git push
↓
CI
↓
Docker Hub
↓
CD
↓
docker compose up -d
↓
Entire stack created
```

---

# Future Deployments

```
git push
↓
CI
↓
Docker Hub
↓
Watchtower
↓
Replace url-app
↓
Discord notification
```

No manual deployment required.

---

# Troubleshooting

## Wrong Docker Hub Username

Error:

```
requested access to the resource is denied
```

Cause:

Wrong namespace.

Fix:

```
syedaftab04/project05-url-shortener
```

---

## Missing Secrets

CI failed.

Fix:

Added:

* DOCKERHUB_USERNAME
* DOCKERHUB_TOKEN

---

## container_name Conflict

Error:

```
container name already in use
```

Fix:

Removed:

```
container_name:
```

from compose file.

---

## Watchtower API Version Error

Error:

```
client version 1.25 too old
```

Fix:

```
DOCKER_API_VERSION=1.54
```

---

## Tests Failed

Cause:

Application version and test version mismatch.

Fix:

Update:

```
tests/test_app.py
```

to match app version.

---

# Future Improvements

AWS EC2

Application Load Balancer

Private Subnets

RDS

Terraform

Self-hosted Runner on EC2

Kubernetes

Helm

ArgoCD

GitOps

---

# Final Flow

```
Developer
↓
Git Push
↓
GitHub Actions CI
(Pytest + Ruff)
↓
Docker Build
↓
Docker Hub
↓
Watchtower
↓
Pull Image
↓
Replace url-app
↓
Discord Notification
↓
Application Updated
```

# Zero-Touch Deployment Achieved 🚀
