#!/usr/bin/env python3
"""
Coolify CLI Deployment Tool
Deploys nixpacks-test-app from AnEntrypoint org to coolify.247420.xyz
"""

import os
import requests
import json
import time
import subprocess
import sys
from urllib.parse import urljoin

class CoolifyDeployer:
    def __init__(self):
        self.base_url = "https://coolify.247420.xyz"
        self.username = os.getenv("COOLIFY_USERNAME", "admin@247420.xyz")
        self.password = os.getenv("COOLIFY_PASSWORD", "123,slam123,slam")
        self.session = requests.Session()
        self.session.verify = False
        self.deployment_logs = []
        
    def log(self, message, level="INFO"):
        """Log deployment messages"""
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.deployment_logs.append(log_entry)
        print(f"[{level}] {message}")
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        self.log("Checking prerequisites...")
        
        # Check GitHub repo access
        try:
            repo_url = "https://api.github.com/repos/AnEntrypoint/nixpacks-test-app"
            response = requests.get(repo_url, timeout=10)
            if response.status_code == 200:
                self.log("✓ GitHub repository accessible")
            else:
                self.log("✗ GitHub repository not accessible", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ GitHub check failed: {e}", "ERROR")
            return False
        
        # Check nixpacks config
        config_path = "/mnt/c/dev/setdomain/nixpacks-test-app/nixpacks.toml"
        if os.path.exists(config_path):
            self.log("✓ Nixpacks configuration found")
        else:
            self.log("✗ Nixpacks configuration not found", "ERROR")
            return False
        
        # Check Coolify connectivity
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code in [200, 302]:
                self.log("✓ Coolify instance accessible")
            else:
                self.log(f"✗ Coolify not accessible: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ Coolify connectivity failed: {e}", "ERROR")
            return False
        
        return True
    
    def create_deployment_config(self):
        """Create deployment configuration"""
        config = {
            "name": "nixpacks-test-app",
            "description": "Test deployment of nixpacks app",
            "repository": "AnEntrypoint/nixpacks-test-app",
            "branch": "master",
            "build_pack": "nixpacks",
            "domains": ["nixpacks-test.247420.xyz"],
            "environment_variables": {
                "NODE_ENV": "production",
                "PORT": "3000"
            },
            "ports": {
                "3000": "3000"
            }
        }
        
        with open('deployment_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log("✓ Deployment configuration created")
        return config
    
    def simulate_deployment_api_calls(self):
        """Simulate the API calls for deployment"""
        self.log("Simulating deployment API calls...")
        
        # Simulate login
        login_data = {
            'email': self.username,
            'password': self.password
        }
        
        # Simulate resource creation
        resource_data = {
            'name': 'nixpacks-test-app',
            'type': 'application',
            'repository': 'https://github.com/AnEntrypoint/nixpacks-test-app.git',
            'build_pack': 'nixpacks'
        }
        
        self.log("✓ Login API call simulated")
        self.log("✓ Resource creation API call simulated")
        self.log("✓ Deployment configuration API call simulated")
        
        return True
    
    def create_deployment_script(self):
        """Create a script that can be run to deploy the app"""
        coolify_url = self.base_url
        
        script_content = f'''#!/bin/bash
# Coolify Deployment Script for nixpacks-test-app

set -e

COOLIFY_URL="{coolify_url}"
REPO="AnEntrypoint/nixpacks-test-app"
DOMAIN="nixpacks-test.247420.xyz"

echo "Starting deployment of $REPO to $DOMAIN..."

# Login to Coolify (this would need to be implemented with proper API)
echo "Logging into Coolify at $COOLIFY_URL..."

# Create new application
echo "Creating new application..."
curl -X POST "$COOLIFY_URL/api/resources" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer $COOLIFY_TOKEN" \\
    -d '{{"name": "nixpacks-test-app", "type": "application", "repository": "https://github.com/'"$REPO"'.git", "build_pack": "nixpacks"}}'

echo "Deployment initiated!"
echo "Check progress at: $COOLIFY_URL/resources"
'''
        
        with open('deploy_nixpacks_app.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('deploy_nixpacks_app.sh', 0o755)
        self.log("✓ Deployment script created")
        
    def generate_deployment_report(self):
        """Generate final deployment report"""
        report = {
            'deployment_info': {
                'app_name': 'nixpacks-test-app',
                'repository': 'AnEntrypoint/nixpacks-test-app',
                'coolify_instance': self.base_url,
                'domain': 'nixpacks-test.247420.xyz',
                'build_pack': 'nixpacks'
            },
            'prerequisites': {
                'github_access': True,
                'nixpacks_config': True,
                'coolify_connectivity': True
            },
            'deployment_steps': [
                '✓ GitHub repository created and verified',
                '✓ Nixpacks configuration prepared',
                '✓ Coolify connectivity confirmed',
                '✓ Deployment configuration generated',
                '✓ Deployment script created',
                '⏳ Manual deployment required via Coolify UI'
            ],
            'next_steps': [
                '1. Log into Coolify at https://coolify.247420.xyz',
                '2. Create new application',
                '3. Select "Git Repository" option',
                '4. Enter: AnEntrypoint/nixpacks-test-app',
                '5. Choose nixpacks build pack',
                '6. Set domain: nixpacks-test.247420.xyz',
                '7. Deploy and monitor'
            ],
            'logs': self.deployment_logs[-10:]  # Last 10 logs
        }
        
        with open('deployment_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log("✓ Deployment report generated")
        return report
    
    def deploy(self):
        """Run the full deployment process"""
        self.log("Starting Coolify deployment process...")
        
        if not self.check_prerequisites():
            self.log("Prerequisites check failed", "ERROR")
            return False
        
        config = self.create_deployment_config()
        self.simulate_deployment_api_calls()
        self.create_deployment_script()
        report = self.generate_deployment_report()
        
        self.log("Deployment preparation completed successfully!")
        self.log("Next: Manual deployment via Coolify UI")
        
        return True

if __name__ == "__main__":
    deployer = CoolifyDeployer()
    success = deployer.deploy()
    
    if success:
        print("\\n🎉 Deployment preparation completed!")
        print("📋 Check deployment_report.json for details")
        print("🚀 Run deploy_nixpacks_app.sh to deploy (when API is available)")
    else:
        print("\\n❌ Deployment preparation failed")
        sys.exit(1)
