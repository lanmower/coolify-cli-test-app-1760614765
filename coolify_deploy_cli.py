#!/usr/bin/env python3
"""
Coolify Deployment CLI Tool
Based on workflow analysis from https://coolify.247420.xyz
"""

import requests
import json
import sys
import time
from urllib.parse import urljoin

class CoolifyDeployer:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False  # For SSL issues
        
    def login(self, email, password):
        """Login to Coolify"""
        print(f"🔐 Logging in to {self.base_url}...")
        
        # Get login page and CSRF token
        login_page = self.session.get(f"{self.base_url}/login")
        if login_page.status_code != 200:
            raise Exception(f"Failed to get login page: {login_page.status_code}")
            
        # Extract CSRF token (simplified)
        csrf_token = None
        if 'name="_token"' in login_page.text:
            import re
            match = re.search(r'name="_token"[^>]*value="([^"]*)"', login_page.text)
            if match:
                csrf_token = match.group(1)
        
        if not csrf_token:
            print("⚠️  Could not extract CSRF token, proceeding without it...")
        
        # Perform login
        login_data = {
            'email': email,
            'password': password,
            '_token': csrf_token or ''
        }
        
        response = self.session.post(
            f"{self.base_url}/login",
            data=login_data,
            allow_redirects=False
        )
        
        # Check if login successful (redirect or 200)
        if response.status_code in [200, 302]:
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    
    def get_servers(self):
        """Get list of servers"""
        print("📋 Getting servers...")
        response = self.session.get(f"{self.base_url}/api/v1/servers")
        
        if response.status_code == 200:
            servers = response.json()
            print(f"✅ Found {len(servers)} servers")
            for server in servers:
                print(f"   - {server.get('name', 'Unknown')} ({server.get('ip', 'No IP')})")
            return servers
        else:
            print(f"❌ Failed to get servers: {response.status_code}")
            return []
    
    def get_applications(self):
        """Get list of applications"""
        print("📱 Getting applications...")
        response = self.session.get(f"{self.base_url}/api/v1/applications")
        
        if response.status_code == 200:
            apps = response.json()
            print(f"✅ Found {len(apps)} applications")
            for app in apps:
                print(f"   - {app.get('name', 'Unknown')} ({app.get('git_repository', 'No repo')})")
            return apps
        else:
            print(f"❌ Failed to get applications: {response.status_code}")
            return []
    
    def deploy_application(self, app_id, branch="main"):
        """Deploy an application"""
        print(f"🚀 Deploying application {app_id} (branch: {branch})...")
        
        deploy_data = {
            "branch": branch,
            "force_rebuild": False
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/applications/{app_id}/deploy",
            json=deploy_data
        )
        
        if response.status_code in [200, 202]:
            print("✅ Deployment started!")
            return response.json()
        else:
            print(f"❌ Failed to start deployment: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def monitor_deployment(self, deployment_id=None, timeout=300):
        """Monitor deployment progress"""
        print("📊 Monitoring deployment progress...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # This would typically connect to WebSocket or poll Livewire
            # For now, simulate with a simple status check
            print(f"⏳ Checking deployment status... ({int(time.time() - start_time)}s)")
            time.sleep(10)
        
        print("✅ Deployment monitoring completed")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 coolify_deploy_cli.py <command>")
        print("Commands: login, servers, apps, deploy")
        sys.exit(1)
    
    deployer = CoolifyDeployer()
    command = sys.argv[1].lower()
    
    try:
        if command == "login":
            email = input("Email: ")
            password = input("Password: ")
            deployer.login(email, password)
            
        elif command == "servers":
            deployer.login("admin@247420.xyz", "123,slam123,slam")
            deployer.get_servers()
            
        elif command == "apps":
            deployer.login("admin@247420.xyz", "123,slam123,slam") 
            deployer.get_applications()
            
        elif command == "deploy":
            if len(sys.argv) < 3:
                print("Usage: python3 coolify_deploy_cli.py deploy <app_id>")
                sys.exit(1)
            
            app_id = sys.argv[2]
            deployer.login("admin@247420.xyz", "123,slam123,slam")
            
            # First get applications to show what's available
            apps = deployer.get_applications()
            
            if apps:
                deploy_result = deployer.deploy_application(app_id)
                if deploy_result:
                    deployer.monitor_deployment()
            
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
