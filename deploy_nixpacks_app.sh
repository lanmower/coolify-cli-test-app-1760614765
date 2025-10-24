#!/bin/bash
# Coolify Deployment Script for nixpacks-test-app

set -e

COOLIFY_URL="https://coolify.247420.xyz"
REPO="AnEntrypoint/nixpacks-test-app"
DOMAIN="nixpacks-test.247420.xyz"

echo "Starting deployment of $REPO to $DOMAIN..."

# Login to Coolify (this would need to be implemented with proper API)
echo "Logging into Coolify at $COOLIFY_URL..."

# Create new application
echo "Creating new application..."
curl -X POST "$COOLIFY_URL/api/resources" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $COOLIFY_TOKEN" \
    -d '{"name": "nixpacks-test-app", "type": "application", "repository": "https://github.com/'"$REPO"'.git", "build_pack": "nixpacks"}'

echo "Deployment initiated!"
echo "Check progress at: $COOLIFY_URL/resources"
