#!/usr/bin/env python3
"""
Improved Coolify Deployment CLI Tool
Better session handling and debugging
"""

import requests
import json
import sys
import time
import urllib3
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ImprovedCoolifyDeployer:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        # Set proper headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def login(self, email, password):
        """Login to Coolify with improved session handling"""
        print(f"🔐 Logging in to {self.base_url}...")

        try:
            # Get login page first to get any session cookies
            print("Getting login page...")
            login_page = self.session.get(f"{self.base_url}/login")
            print(f"Login page status: {login_page.status_code}")
            
            if login_page.status_code != 200:
                raise Exception(f"Failed to get login page: {login_page.status_code}")

            print(f"Session cookies after login page: {list(self.session.cookies.keys())}")

            # Extract CSRF token
            csrf_token = None
            if '_token' in login_page.text:
                import re
                match = re.search(r'name="_token"[^>]*value="([^"]*)"', login_page.text)
                if match:
                    csrf_token = match.group(1)
                    print(f"CSRF token found: {csrf_token[:20]}...")

            if not csrf_token:
                print("⚠️  Could not extract CSRF token, proceeding without it...")

            # Perform login with redirects allowed to get proper session
            login_data = {
                'email': email,
                'password': password,
                '_token': csrf_token or ''
            }

            print("Attempting login...")
            response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                allow_redirects=True  # Allow redirects to set cookies properly
            )
            
            print(f"Login response status: {response.status_code}")
            print(f"Final URL: {response.url}")
            print(f"Session cookies after login: {list(self.session.cookies.keys())}")

            # Check if login was successful by looking for dashboard indicators
            if response.status_code == 200 and ('dashboard' in response.text.lower() or 'logout' in response.text.lower()):
                print("✅ Login successful!")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"Response preview: {response.text[:300]}")
                return False

        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def get_servers(self):
        """Get list of servers with improved error handling"""
        print("📋 Getting servers...")
        
        try:
            # Try different endpoints
            endpoints = [
                "/api/v1/servers",
                "/api/servers", 
                "/servers"
            ]
            
            for endpoint in endpoints:
                url = f"{self.base_url}{endpoint}"
                print(f"Trying endpoint: {url}")
                
                response = self.session.get(url)
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        servers = response.json()
                        if isinstance(servers, list):
                            print(f"✅ Found {len(servers)} servers")
                            for server in servers:
                                print(f"   - {server.get('name', 'Unknown')} ({server.get('ip', 'No IP')})")
                            return servers
                    except json.JSONDecodeError:
                        print(f"Response is not JSON: {response.text[:200]}")
                elif response.status_code == 401:
                    print("❌ Authentication failed - session may be expired")
                else:
                    print(f"Failed with status: {response.status_code}")
                    
            print("❌ All endpoints failed")
            return []
            
        except Exception as e:
            print(f"❌ Error getting servers: {e}")
            return []

    def get_applications(self):
        """Get list of applications"""
        print("📋 Getting applications...")
        
        try:
            endpoints = [
                "/api/v1/applications",
                "/api/applications",
                "/applications"
            ]
            
            for endpoint in endpoints:
                url = f"{self.base_url}{endpoint}"
                print(f"Trying applications endpoint: {url}")
                
                response = self.session.get(url)
                print(f"Applications response status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        apps = response.json()
                        if isinstance(apps, list):
                            print(f"✅ Found {len(apps)} applications")
                            for app in apps:
                                print(f"   - {app.get('name', 'Unknown')} ({app.get('uuid', 'No UUID')})")
                            return apps
                    except json.JSONDecodeError:
                        print(f"Response is not JSON: {response.text[:200]}")
                else:
                    print(f"Failed with status: {response.status_code}")
                    
            print("❌ All application endpoints failed")
            return []
            
        except Exception as e:
            print(f"❌ Error getting applications: {e}")
            return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 improved_coolify_cli.py <command>")
        print("Commands: login, servers, apps")
        sys.exit(1)

    deployer = ImprovedCoolifyDeployer()
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

        else:
            print(f"Unknown command: {command}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
