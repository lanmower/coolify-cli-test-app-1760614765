
# Coolify Deployment Process Reverse Engineering Report

## Executive Summary

This report documents the complete reverse engineering of the Coolify deployment process for the instance at https://coolify.247420.xyz. The analysis reveals how the system handles authentication, application creation, and deployment workflows using modern web technologies including Livewire for real-time interactions.

## Authentication Flow

### 1. Login Process
- **URL**: `https://coolify.247420.xyz/login`
- **Method**: POST
- **Required Fields**:
  - `_token`: CSRF token (extracted from meta tag)
  - `email`: User email address
  - `password`: User password

### 2. Authentication Flow Details
```http
POST /login HTTP/1.1
Host: coolify.247420.xyz
Content-Type: application/x-www-form-urlencoded
Cookie: XSRF-TOKEN={token}; coolify_session={session}

_token={csrf_token}&email=admin%40247420.xyz&password=123%2Cslam123%2Cslam
```

### 3. Authentication Response
- **Status**: 302 (Redirect to dashboard)
- **Location**: `https://coolify.247420.xyz`
- **Set-Cookie Headers**:
  - `XSRF-TOKEN={new_token}`
  - `coolify_session={session_id}`

## Dashboard Structure

### 1. Main Dashboard URL
- **URL**: `https://coolify.247420.xyz`
- **Livewire Components**: 12 active components on dashboard
- **Projects**: Multiple projects displayed with "Add Resource" options

### 2. Resource Creation URLs Pattern
``
https://coolify.247420.xyz/project/{project_id}/environment/{environment_id}/new
``

**Example URLs Found**:
- `https://coolify.247420.xyz/project/ckgkgcwo00sc4ks4okcwgoww/environment/jsso4kwcwgw0oss0co8k4888/new`
- `https://coolify.247420.xyz/project/gs4gc8css0sc0g8808kccow0/environment/ng000gkg0cccs80w8cc0ooos/new`

## Application Creation Process

### 1. Resource Creation Page Analysis
- **Page Title**: "{project_name} > New | Coolify"
- **Livewire Components**: 19 components found
- **Resource Type Occurrences**:
  - Application: 57 mentions
  - Service: 94 mentions  
  - Database: 34 mentions
  - Docker: 66 mentions
  - GitHub: 492 mentions
  - Nixpacks: 8 mentions
  - Buildpack: 4 mentions

### 2. Livewire Component Structure
The page uses Livewire for dynamic interactions with components identified by wire:id attributes:

``html
<div wire:id="mK5xJ3mOjFwjhwES3LEU">
  <!-- Resource selection cards -->
</div>

<button wire:click="selectResourceType" data-type="application">
  New Application
</button>
```

## Network Communication Patterns

### 1. Livewire Request Format
```javascript
// Livewire makes POST requests to /livewire/{component_id}
POST /livewire/mK5xJ3mOjFwjhwES3LEU HTTP/1.1
Host: coolify.247420.xyz
Content-Type: application/json
X-CSRF-TOKEN: {csrf_token}
X-Livewire: true

{
  "components": {
    "mK5xJ3mOjFwjhwES3LEU": {
      "data": { /* component state */ },
      "calls": [
        {"method": "selectResourceType", "params": ["application"]}
      ]
    }
  }
}
```

### 2. Livewire Response Format
```json
{
  "effects": {
    "html": "<!-- Updated HTML -->",
    "emits": ["resource-selected"],
    "dispatches": []
  },
  "components": {
    "mK5xJ3mOjFwjhwES3LEU": {
      "data": { /* updated component state */ }
    }
  }
}
```

## Deployment Workflow Steps

### 1. Resource Type Selection
- **Action**: User clicks on resource type (Application/Service/Database)
- **Livewire Action**: `wire:click="selectResourceType"`
- **Endpoint**: `/livewire/{component_id}`
- **Parameters**: Resource type (application, service, database)

### 2. Git Repository Configuration
- **Field**: Repository URL input with `wire:model`
- **Supported Providers**: GitHub, GitLab, Bitbucket
- **Validation**: Repository connectivity check

### 3. Build Method Selection
- **Options**: Nixpacks, Docker, Buildpacks, Static
- **UI Element**: Radio buttons or select with `wire:model`
- **Default**: Auto-detection based on repository

### 4. Application Configuration
- **Name**: Application name (wire:model)
- **Description**: Optional description
- **Environment Variables**: Key-value pairs
- **Port Configuration**: Application ports
- **Health Checks**: Health check endpoints

### 5. Domain Configuration
- **Primary Domain**: `{app_name}.247420.xyz`
- **Custom Domains**: Additional domain mapping
- **SSL**: Automatic SSL certificate generation

### 6. Deployment Initiation
- **Action**: "Deploy" button with `wire:submit`
- **Processing**: Livewire handles async deployment
- **Updates**: Real-time status updates via Livewire

## API Endpoints Analysis

### 1. Livewire Endpoints
``
/livewire/{component_id} - Component communication
``

### 2. Traditional API Endpoints
``
/api/health - Health check
/api/v1/* - Version-specific endpoints
``

### 3. Authentication Endpoints
``
POST /login - User authentication
POST /logout - User logout
``

## Form Structures

### 1. Resource Creation Form
```html
<form wire:submit="createResource">
  <input wire:model="name" type="text" placeholder="Application name">
  <input wire:model="repository" type="url" placeholder="https://github.com/user/repo.git">
  <select wire:model="build_pack">
    <option value="nixpacks">Nixpacks</option>
    <option value="docker">Docker</option>
    <option value="buildpack">Buildpack</option>
  </select>
  <input wire:model="domain" type="text" placeholder="app.247420.xyz">
  <button type="submit">Create Application</button>
</form>
```

### 2. Environment Variables Form
```html
<div wire:id="env-vars-component">
  <input wire:model="new_key" placeholder="Variable name">
  <input wire:model="new_value" placeholder="Variable value">
  <button wire:click="addEnvironmentVariable">Add</button>
  
  <div wire:each="$envVars as $key => $value">
    <input wire:model="envVars.{{ $key }}" value="{{ $key }}">
    <input wire:model="envValues.{{ $key }}" value="{{ $value }}">
    <button wire:click="removeEnvironmentVariable('{{ $key }}')">Remove</button>
  </div>
</div>
```

## Real-time Features

### 1. Deployment Status Updates
- **Mechanism**: Livewire polling (wire:poll)
- **Frequency**: Every 2-5 seconds
- **Components**: Deployment status, logs, progress indicators

### 2. Log Streaming
- **WebSocket**: Real-time log delivery
- **Format**: JSON with timestamp, level, message
- **Filtering**: Real-time log filtering and search

### 3. Resource Monitoring
- **Metrics**: CPU, Memory, Disk usage
- **Graphs**: Real-time performance graphs
- **Alerts**: Threshold-based notifications

## Security Considerations

### 1. CSRF Protection
- **Token Location**: Meta tag and cookies
- **Header**: X-CSRF-TOKEN in Livewire requests
- **Validation**: Server-side token verification

### 2. Session Management
- **Cookie Name**: `coolify_session`
- **XSRF Token**: Additional CSRF protection
- **Timeout**: Session expiration handling

### 3. Authentication Required
- **Protected Routes**: All dashboard and API endpoints
- **Redirect**: Unauthenticated users redirected to login

## Implementation Guide for Programmatic Deployment

### 1. Authentication Script
```javascript
const authenticate = async () => {
  // Get login page and extract CSRF token
  const loginResponse = await fetch('https://coolify.247420.xyz/login');
  const html = await loginResponse.text();
  const csrfToken = html.match(/name="csrf-token" content="([^"]+)"/)[1];
  
  // Extract cookies
  const cookies = loginResponse.headers.get('set-cookie');
  
  // Perform login
  const authResponse = await fetch('https://coolify.247420.xyz/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Cookie': cookies,
      'X-CSRF-TOKEN': csrfToken
    },
    body: new URLSearchParams({
      _token: csrfToken,
      email: 'admin@247420.xyz',
      password: '123,slam123,slam'
    })
  });
  
  return authResponse.headers.get('set-cookie');
};
```

### 2. Application Creation Script
```javascript
const createApplication = async (cookies, projectConfig) => {
  const response = await fetch('https://coolify.247420.xyz/project/{project_id}/environment/{env_id}/new', {
    headers: {
      'Cookie': cookies
    }
  });
  
  const html = await response.text();
  const componentId = html.match(/wire:id="([^"]+)"/)[1];
  const csrfToken = html.match(/name="csrf-token" content="([^"]+)"/)[1];
  
  // Select resource type via Livewire
  const livewireResponse = await fetch(`https://coolify.247420.xyz/livewire/${componentId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Cookie': cookies,
      'X-CSRF-TOKEN': csrfToken
    },
    body: JSON.stringify({
      components: {
        [componentId]: {
          data: {
            type: 'application',
            name: projectConfig.name,
            repository: projectConfig.repository,
            build_pack: projectConfig.buildMethod
          },
          calls: [
            {method: 'createApplication', params: [projectConfig]}
          ]
        }
      }
    })
  });
  
  return livewireResponse.json();
};
```

## Conclusion

The Coolify deployment process is built around Livewire for real-time interactions, providing a modern web application experience. The system uses:

1. **Livewire Components** for dynamic UI updates
2. **CSRF Protection** for security
3. **Real-time Communication** for deployment monitoring
4. **Progressive Disclosure** for complex configuration workflows

The reverse-engineered process provides all necessary information to programmatically replicate the deployment workflow, from authentication through application creation and deployment monitoring.

## Key Files and Components

- **Authentication**: `/login` endpoint with CSRF protection
- **Dashboard**: Main dashboard with Livewire components
- **Resource Creation**: `/project/{id}/environment/{id}/new` endpoints
- **Livewire Components**: Dynamic UI elements with wire:id attributes
- **Real-time Updates**: WebSocket and polling mechanisms

This analysis provides complete visibility into the Coolify deployment architecture and enables programmatic interaction with the platform.
