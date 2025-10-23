# One-Step Coolify Deployment

A CLI tool for one-step deployment to Coolify with automatic GitHub deploy key setup and domain configuration.

## Features

- ✅ Automatic authentication with Coolify
- ✅ GitHub deploy key setup using `gh` CLI
- ✅ Environment creation
- ✅ Application deployment
- ✅ Domain configuration via HTTP requests
- ✅ Zero dependencies - pure Node.js

## Prerequisites

1. Node.js 16+
2. GitHub CLI (`gh`) installed and authenticated
3. Coolify instance access

## Installation

```bash
# Clone or download deploy.js
chmod +x deploy.js
```

## Usage

```bash
# Set environment variables
export COOLIFY_USERNAME="your-coolify-username"
export COOLIFY_PASSWORD="your-coolify-password"

# Run deployment
node deploy.js

# Or with parameters
node deploy.js --repo=https://github.com/user/repo --domain=domain.example.com
```

## Environment Variables

- `COOLIFY_USERNAME`: Coolify username (or `U` for backward compatibility)
- `COOLIFY_PASSWORD`: Coolify password (or `P` for backward compatibility)

## What It Does

1. **Authentication**: Logs into your Coolify instance
2. **Project Setup**: Uses existing project or creates new one
3. **GitHub Integration**: Sets up deploy key using `gh` CLI
4. **Environment**: Creates production environment
5. **Application**: Deploys the application
6. **Domain**: Configures custom domain (when application is available)

## Output

The tool provides:
- ✅ Success confirmation for each step
- 🔗 Direct URLs to created resources
- 📝 Manual setup instructions if automation fails

## Example Output

```
🎯 Starting One-Step Deployment...
✅ Login successful
✅ Found existing project: ko4gsw80socs0088ks8w4s4s
✅ SSH key pair generated
✅ Deploy key added to GitHub repository
✅ Environment created successfully
✅ Environment ID: nggwwoggokg8gokws0gogsg0

🎉 One-Step Deployment Completed!
🌐 Access URLs:
  📋 Coolify Dashboard: https://coolify.example.com/project/ko4gsw80socs0088ks8w4s4s
  🏗️ Environment: https://coolify.example.com/project/ko4gsw80socs0088ks8w4s4s/environment/nggwwoggokg8gokws0gogsg0
```

## Troubleshooting

- **Authentication fails**: Verify Coolify URL and credentials
- **GitHub CLI fails**: Ensure `gh` is installed and authenticated
- **Environment creation fails**: Check project permissions
- **Domain configuration**: Requires successful application deployment

## License

MIT