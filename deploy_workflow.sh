#!/bin/bash
# Complete Coolify Deployment Workflow Script

echo "🚀 COOLIFY DEPLOYMENT WORKFLOW"
echo "================================"

# Configuration
COOLIFY_URL="https://coolify.247420.xyz"
EMAIL="admin@247420.xyz"  
PASSWORD="123,slam123,slam"

# Step 1: Login
echo "1. Logging in..."
SESSION_FILE="coolify_session.txt"

# Get CSRF token and login
curl -s -c "$SESSION_FILE" "$COOLIFY_URL/login" > login_page.html
CSRF_TOKEN=$(grep -o 'name="_token"[^>]*value="[^"]*"' login_page.html | sed 's/.*value="\([^"]*\)".*/\1/' | head -1)

LOGIN_RESPONSE=$(curl -s -b "$SESSION_FILE" -c "$SESSION_FILE" \
  -X POST "$COOLIFY_URL/login" \
  -d "email=$EMAIL" \
  -d "password=$PASSWORD" \
  -d "_token=$CSRF_TOKEN" \
  -w "HTTP_CODE:%{http_code}")

if echo "$LOGIN_RESPONSE" | grep -q "HTTP_CODE:302\|HTTP_CODE:200"; then
    echo "✅ Login successful!"
else
    echo "❌ Login failed!"
    exit 1
fi

# Step 2: Get servers
echo -e "\n2. Getting servers..."
SERVERS=$(curl -s -b "$SESSION_FILE" "$COOLIFY_URL/api/v1/servers")
echo "$SERVERS" | jq '.' 2>/dev/null || echo "$SERVERS"

# Step 3: Get applications  
echo -e "\n3. Getting applications..."
APPLICATIONS=$(curl -s -b "$SESSION_FILE" "$COOLIFY_URL/api/v1/applications")
echo "$APPLICATIONS" | jq '.' 2>/dev/null || echo "$APPLICATIONS"

# Step 4: Extract application IDs and show options
if command -v jq >/dev/null 2>&1; then
    APP_IDS=$(echo "$APPLICATIONS" | jq -r '.[].id' 2>/dev/null)
    if [ -n "$APP_IDS" ]; then
        echo -e "\n4. Available applications:"
        echo "$APPLICATIONS" | jq -r '.[] | "ID: \(.id) - Name: \(.name // "Unknown") - Repo: \(.git_repository // "N/A")"'
        
        # Try to deploy the first application
        FIRST_APP_ID=$(echo "$APPLICATIONS" | jq -r '.[0].id' 2>/dev/null)
        if [ -n "$FIRST_APP_ID" ] && [ "$FIRST_APP_ID" != "null" ]; then
            echo -e "\n5. Attempting to deploy application ID: $FIRST_APP_ID"
            
            DEPLOY_RESPONSE=$(curl -s -b "$SESSION_FILE" \
              -X POST "$COOLIFY_URL/api/v1/applications/$FIRST_APP_ID/deploy" \
              -H "Content-Type: application/json" \
              -d '{"branch":"main","force_rebuild":false}' \
              -w "HTTP_CODE:%{http_code}")
            
            echo "Deploy response: $DEPLOY_RESPONSE"
            
            if echo "$DEPLOY_RESPONSE" | grep -q "HTTP_CODE:200\|HTTP_CODE:202"; then
                echo "✅ Deployment started successfully!"
            else
                echo "❌ Deployment failed"
            fi
        fi
    fi
fi

# Cleanup
rm -f login_page.html "$SESSION_FILE"
echo -e "\n✅ Workflow completed!"
