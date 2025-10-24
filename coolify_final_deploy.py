#!/usr/bin/env python3
"""
Final Coolify Deployment CLI Tool
Working version based on session cookie authentication
"""

import requests
import re
import json
import sys
import argparse
from urllib.parse import urljoin

class CoolifyAPI:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False  # Ignore SSL warnings
        self.csrf_token = None
        
    def login(self, email, password):
        """Login and establish session"""
        print(f"🔐 Logging in to {self.base_url}...")
        
        try:
            # Get login page and CSRF token
            response = self.session.get(f"{self.base_url}/login")
            response.raise_for_status()
            
            # Extract CSRF token
            csrf_match = re.search(r'name="_token"[^>]*value="([^"]*)"', response.text)
            self.csrf_token = csrf_match.group(1) if csrf_match else None
            
            if not self.csrf_token:
                print("⚠️  Could not extract CSRF token")
                return False
            
            # Perform login
            login_data = {
                'email': email,
                'password': password,
                '_token': self.csrf_token
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                allow_redirects=False
            )
            
            # Check if login was successful (302 redirect or 200)
            if response.status_code in [200, 302]:
                print("✅ Login successful!")
                
                # Follow redirect to establish session
                if response.status_code == 302:
                    redirect_url = response.headers.get('Location', '/')
                    self.session.get(urljoin(self.base_url, redirect_url))
                
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_authentication(self):
        """Test if our session is working"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/servers")
            if response.status_code == 200:
                print("✅ Session authenticated!")
                return True
            else:
                print(f"❌ Session not authenticated: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            return False
    
    def get_servers(self):
        """Get list of servers"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/servers")
            if response.status_code == 200:
                servers = response.json()
                print(f"✅ Found {len(servers)} servers")
                for server in servers:
                    name = server.get('name', 'Unknown')
                    ip = server.get('ip', 'No IP')
                    status = server.get('status', 'Unknown')
                    print(f"   - {name} ({ip}) - Status: {status}")
                return servers
            else:
                print(f"❌ Failed to get servers: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting servers: {e}")
            return []
    
    def get_applications(self):
        """Get list of applications"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/applications")
            if response.status_code == 200:
                apps = response.json()
                print(f"✅ Found {len(apps)} applications")
                for app in apps:
                    name = app.get('name', 'Unknown')
                    repo = app.get('git_repository', 'No repo')
                    status = app.get('status', 'Unknown')
                    print(f"   - {name} ({repo}) - Status: {status}")
                return apps
            else:
                print(f"❌ Failed to get applications: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting applications: {e}")
            return []
    
    def deploy_application(self, app_id, branch="main", force_rebuild=False):
        """Deploy an application"""
        try:
            print(f"🚀 Deploying application {app_id} (branch: {branch})...")
            
            deploy_data = {
                "branch": branch,
                "force_rebuild": force_rebuild
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/applications/{app_id}/deploy",
                json=deploy_data
            )
            
            if response.status_code in [200, 202]:
                result = response.json()
                print("✅ Deployment started successfully!")
                print(f"   Deployment ID: {result.get('id', 'Unknown')}")
                return result
            else:
                print(f"❌ Failed to start deployment: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error deploying application: {e}")
            return None
    
    def create_application(self, name, git_repository, branch="main"):
        """Create a new application"""
        try:
            print(f"📱 Creating application: {name}")
            
            app_data = {
                "name": name,
                "git_repository": git_repository,
                "branch": branch,
                "build_pack": "nixpacks"  # Default build pack
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/applications",
                json=app_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ Application created successfully!")
                print(f"   Application ID: {result.get('id', 'Unknown')}")
                return result
            else:
                print(f"❌ Failed to create application: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating application: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Coolify Deployment CLI')
    parser.add_argument('command', choices=['login', 'test', 'servers', 'apps', 'deploy', 'create'], 
                       help='Command to execute')
    parser.add_argument('--email', default='admin@247420.xyz', help='Email for login')
    parser.add_argument('--password', default='123,slam123,slam', help='Password for login')
    parser.add_argument('--app-id', type=int, help='Application ID for deployment')
    parser.add_argument('--branch', default='main', help='Git branch')
    parser.add_argument('--name', help='Application name (for create)')
    parser.add_argument('--repo', help='Git repository URL (for create)')
    parser.add_argument('--force', action='store_true', help='Force rebuild')
    
    args = parser.parse_args()
    
    api = CoolifyAPI()
    
    try:
        if args.command == 'login':
            success = api.login(args.email, args.password)
            if success:
                api.test_authentication()
            sys.exit(0 if success else 1)
            
        elif args.command == 'test':
            if api.login(args.email, args.password):
                api.test_authentication()
            else:
                sys.exit(1)
                
        elif args.command == 'servers':
            if api.login(args.email, args.password):
                api.get_servers()
            else:
                sys.exit(1)
                
        elif args.command == 'apps':
            if api.login(args.email, args.password):
                api.get_applications()
            else:
                sys.exit(1)
                
        elif args.command == 'deploy':
            if not args.app_id:
                print("❌ --app-id is required for deploy command")
                sys.exit(1)
                
            if api.login(args.email, args.password):
                api.deploy_application(args.app_id, args.branch, args.force)
            else:
                sys.exit(1)
                
        elif args.command == 'create':
            if not args.name or not args.repo:
                print("❌ --name and --repo are required for create command")
                sys.exit(1)
                
            if api.login(args.email, args.password):
                api.create_application(args.name, args.repo, args.branch)
            else:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
