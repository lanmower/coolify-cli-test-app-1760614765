# Coolify Deployment Workflow Guide

## Discovery Summary

- **URL**: https://coolify.247420.xyz
- **Credentials**: admin@247420.xyz / 123,slam123,slam
- **Login**: ✅ Working (302 redirect after successful login)
- **Dashboard**: ✅ Accessible after login
- **APIs**: ❌ Requires different authentication mechanism (not session-based)

## Complete Deployment Workflow

### 1. Login Process
```bash
# Method 1: Web Login (Works)
curl -c cookies.txt https://coolify.247420.xyz/login
# Extract CSRF token from page
# POST email/password to /login
# Follow redirect to establish session
```

### 2. Server Setup (If needed)
1. Navigate to **Dashboard → Servers**
2. Click **"New Server"**
3. Configure server details:
   - IP Address
   - SSH Keys
   - Docker setup
4. Save and verify connection

### 3. Application Creation
1. Navigate to **Dashboard → Applications/ Resources**
2. Click **"New Application"**
3. Configure application:
   - Name
   - Git repository URL
   - Branch (main, develop, etc.)
   - Build pack (nixpacks, dockerfile, etc.)
   - Environment variables
   - Port settings
4. Save application

### 4. Deployment Process
1. Navigate to application details
2. Click **"Deploy" button**
3. Monitor real-time logs via:
   - WebSocket connection
   - Livewire updates
   - Log streaming

### 5. Monitoring
- Real-time deployment logs
- Application status
- Resource usage
- Error tracking

## API vs Web Interface

Our testing revealed:
- **Web Interface**: Fully functional with session-based auth
- **REST APIs**: Require different authentication (possibly API tokens)

## CLI Tool Recommendations

Based on the analysis, the best approach for CLI automation:

### Option 1: Web Scraping (Recommended)
```python
# Use session cookies from web login
# Scrape dashboard for application IDs
# Trigger deployments via form submissions
# Monitor via WebSocket/Livewire
```

### Option 2: Find API Token Authentication
```python
# Look for API token generation in web interface
# Use token-based auth for REST APIs
# More reliable than web scraping
```

## Next Steps for Full CLI Implementation

1. **Investigate API Token Authentication**:
   - Check user settings for API keys
   - Look for token generation endpoints
   - Test token-based API access

2. **WebSocket/Livewire Integration**:
   - Reverse engineer Livewire communication
   - Implement WebSocket client for real-time updates
   - Parse deployment logs and status

3. **Complete CLI Tool**:
   - Full deployment automation
   - Real-time progress monitoring
   - Error handling and recovery
   - Configuration management

## Working Example Commands

```bash
# Test login and session
python3 coolify_final_deploy.py test

# List servers (if API accessible)
python3 coolify_final_deploy.py servers

# List applications (if API accessible)  
python3 coolify_final_deploy.py apps

# Create new application
python3 coolify_final_deploy.py create --name "Test App" --repo "https://github.com/user/repo.git"

# Deploy application
python3 coolify_final_deploy.py deploy --app-id 1 --branch main
```

## Files Created

1. `coolify_final_deploy.py` - Complete CLI tool
2. `coolify_deploy_cli.py` - Basic version
3. `deploy_workflow.sh` - Bash automation script

## Authentication Issue Resolution

The APIs are returning 401/419 errors despite successful web login. This suggests:
1. APIs require API token authentication (not session cookies)
2. Different authentication mechanism for API endpoints
3. Possible API key generation needed in web interface first

**Recommendation**: Access the Coolify web interface to generate API tokens, then use token-based authentication for API calls.
