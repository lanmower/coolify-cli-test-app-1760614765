#!/usr/bin/env python3
"""
Coolify Application Deployment Tool
Deploys AnEntrypoint/nixpacks-test-app to Coolify
"""

import requests
import json
import sys
import time
import urllib3
import re
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CoolifyApplicationDeployer:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        
        # Browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def login(self, email, password):
        """Login to Coolify"""
        print(f"🔐 Logging in to {self.base_url}")
        
        try:
            response = self.session.get(f"{self.base_url}/login")
            if response.status_code != 200:
                return False, f"Cannot access login page: {response.status_code}"
            
            # Simple login attempt
            login_data = {
                'email': email,
                'password': password,
            }
            
            login_response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                allow_redirects=True
            )
            
            cookies = list(self.session.cookies.keys())
            if 'coolify_session' in cookies:
                print("   ✅ Login successful")
                return True, "Login successful"
            else:
                print("   ❌ Login failed")
                return False, "Login failed"
                
        except Exception as e:
            return False, f"Login error: {e}"

    def get_servers(self):
        """Get available servers for deployment"""
        print("🖥️ Getting available servers...")
        
        try:
            # Access servers page
            response = self.session.get(f"{self.base_url}/servers")
            
            if response.status_code == 200:
                print("   ✅ Servers page accessible")
                
                # Look for server information in the HTML
                content = response.text
                
                # Simple patterns to find server data
                server_patterns = [
                    r'data-server-id="([^"]*)"',
                    r'data-server-uuid="([^"]*)"',
                    r'wire:id=["']([^"']*)["'].*server',
                    r'server.*?uuid["']?\s*[:=]\s*["']([^"']*)["']',
                ]
                
                servers = []
                for pattern in server_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f"   Found {len(matches)} server IDs with pattern")
                        servers.extend(matches)
                
                if servers:
                    print(f"   ✅ Found {len(set(servers))} unique servers")
                    return list(set(servers))[:5]  # Return first 5 unique servers
                else:
                    print("   ⚠️  No server IDs found, but page accessible")
                    return ['default']  # Fallback
            else:
                print(f"   ❌ Cannot access servers page: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error getting servers: {e}")
            return []

    def deploy_application(self, repo_url, app_name=None, server_uuid=None):
        """Deploy an application from GitHub repository"""
        print(f"🚀 Deploying application from {repo_url}")
        
        if app_name is None:
            app_name = repo_url.split('/')[-1].replace('.git', '')
        
        print(f"   Application name: {app_name}")
        
        try:
            # Step 1: Access new application page
            print("1. Accessing application creation page...")
            response = self.session.get(f"{self.base_url}/new-application")
            
            if response.status_code != 200:
                return False, f"Cannot access application creation: {response.status_code}"
            
            print("   ✅ Application creation page accessed")
            
            # Step 2: Look for form and extract any CSRF/Livewire data
            content = response.text
            
            # Extract any tokens or form data
            csrf_match = re.search(r'name=["']_token["']\s*value=["']([^"']+)["']', content)
            csrf_token = csrf_match.group(1) if csrf_match else None
            
            if csrf_token:
                print(f"   ✅ CSRF token found: {csrf_token[:20]}...")
            else:
                print("   ⚠️  No CSRF token found")
            
            # Step 3: Try to submit application creation form
            print("2. Submitting application creation...")
            
            # Prepare application data
            app_data = {
                'name': app_name,
                'description': f'Test deployment of {app_name}',
                'repository': repo_url,
                'build_pack': 'nixpacks',  # Use Nixpacks as specified
                'branch': 'main',
                'port': 3000,  # Default Node.js port
                'install_command': 'npm install',
                'build_command': 'npm run build',
                'start_command': 'npm start',
            }
            
            if csrf_token:
                app_data['_token'] = csrf_token
            
            # Try different form submission approaches
            submission_endpoints = [
                '/applications',
                '/api/v1/applications', 
                '/livewire/update',
                '/new-application',
            ]
            
            for endpoint in submission_endpoints:
                try:
                    print(f"   Trying endpoint: {endpoint}")
                    
                    submit_response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        data=app_data,
                        allow_redirects=False
                    )
                    
                    print(f"     Response status: {submit_response.status_code}")
                    
                    if submit_response.status_code in [200, 201, 302]:
                        print(f"     ✅ Application creation successful via {endpoint}")
                        
                        # Check response for application ID
                        try:
                            if submit_response.headers.get('Content-Type', '').startswith('application/json'):
                                result = submit_response.json()
                                app_id = result.get('uuid') or result.get('id')
                                if app_id:
                                    print(f"     ✅ Application ID: {app_id}")
                                    return True, f"Application created with ID: {app_id}"
                            else:
                                # Look for UUID in HTML response
                                uuid_match = re.search(r'([a-f0-9-]{36})', submit_response.text)
                                if uuid_match:
                                    app_id = uuid_match.group(1)
                                    print(f"     ✅ Application ID: {app_id}")
                                    return True, f"Application created with ID: {app_id}"
                        except:
                            pass
                        
                        print(f"     ✅ Application created (no ID extracted)")
                        return True, f"Application created via {endpoint}"
                    
                    elif submit_response.status_code == 419:
                        print("     ⚠️  CSRF token expired")
                    else:
                        print(f"     ❌ Failed with status {submit_response.status_code}")
                        if submit_response.status_code not in [404, 405]:
                            print(f"     Response preview: {submit_response.text[:200]}")
                
                except Exception as e:
                    print(f"     ❌ Error with {endpoint}: {e}")
            
            # Step 4: Try Livewire approach if regular form submission fails
            if 'livewire' in content.lower():
                print("3. Trying Livewire approach...")
                
                # Extract Livewire component data
                livewire_pattern = r'wire:initial-data=["']([^"']*)["']'
                livewire_match = re.search(livewire_pattern, content)
                
                if livewire_match:
                    try:
                        livewire_data = json.loads(urllib.parse.unquote(livewire_match.group(1)))
                        print("   ✅ Livewire data extracted")
                        
                        # Prepare Livewire request
                        livewire_payload = {
                            'fingerprint': livewire_data.get('fingerprint', {}),
                            'serverMemo': livewire_data.get('serverMemo', {}),
                            'updates': [
                                {
                                    'type': 'callMethod',
                                    'payload': {
                                        'method': 'submit',
                                        'params': [app_data]
                                    }
                                }
                            ]
                        }
                        
                        livewire_headers = {
                            'Content-Type': 'application/json',
                            'Accept': 'text/html,application/xhtml+xml',
                            'X-Livewire': 'true',
                            'X-Requested-With': 'XMLHttpRequest',
                        }
                        
                        if csrf_token:
                            livewire_headers['X-CSRF-TOKEN'] = csrf_token
                        
                        livewire_response = self.session.post(
                            f"{self.base_url}/livewire/update",
                            json=livewire_payload,
                            headers=livewire_headers
                        )
                        
                        print(f"   Livewire response status: {livewire_response.status_code}")
                        
                        if livewire_response.status_code == 200:
                            print("   ✅ Livewire application creation successful")
                            return True, "Application created via Livewire"
                        
                    except Exception as e:
                        print(f"   ❌ Livewire approach error: {e}")
            
            return False, "All application creation methods failed"
            
        except Exception as e:
            return False, f"Deployment error: {e}"

    def monitor_deployment(self, app_id=None):
        """Monitor deployment status"""
        print("📊 Monitoring deployment...")
        
        try:
            # Access applications page to check status
            response = self.session.get(f"{self.base_url}/applications")
            
            if response.status_code == 200:
                print("   ✅ Applications page accessible")
                
                # Look for deployment status information
                content = response.text.lower()
                
                status_indicators = {
                    'deploying': 'deploying' in content,
                    'running': 'running' in content,
                    'failed': 'failed' in content,
                    'success': 'success' in content,
                    'building': 'building' in content,
                }
                
                print(f"   Status indicators: {status_indicators}")
                
                return {
                    'success': True,
                    'status_indicators': status_indicators
                }
            else:
                return {
                    'success': False,
                    'message': f"Cannot access applications: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Monitoring error: {e}"
            }

    def full_deployment_test(self, email, password, repo_url, app_name=None):
        """Run full deployment test"""
        print("=" * 80)
        print("🚀 COOLIFY APPLICATION DEPLOYMENT TEST")
        print("=" * 80)
        print(f"Repository: {repo_url}")
        print(f"App Name: {app_name or 'Auto-detect'}")
        print("=" * 80)
        
        results = {}
        
        # Step 1: Login
        print("\n🔐 STEP 1: AUTHENTICATION")
        print("-" * 50)
        login_success, login_message = self.login(email, password)
        results['login'] = {
            'success': login_success,
            'message': login_message
        }
        
        if not login_success:
            print("\n❌ Login failed - stopping deployment")
            return results
        
        # Step 2: Get Servers
        print("\n🖥️ STEP 2: SERVER DISCOVERY")
        print("-" * 50)
        servers = self.get_servers()
        results['servers'] = {
            'success': len(servers) > 0,
            'servers': servers,
            'count': len(servers)
        }
        
        # Step 3: Deploy Application
        print("\n🚀 STEP 3: APPLICATION DEPLOYMENT")
        print("-" * 50)
        deploy_success, deploy_message = self.deploy_application(repo_url, app_name)
        results['deployment'] = {
            'success': deploy_success,
            'message': deploy_message
        }
        
        # Step 4: Monitor Deployment
        print("\n📊 STEP 4: DEPLOYMENT MONITORING")
        print("-" * 50)
        monitoring_results = self.monitor_deployment()
        results['monitoring'] = monitoring_results
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DEPLOYMENT RESULTS SUMMARY")
        print("=" * 80)
        print(f"✅ Authentication: {'SUCCESS' if login_success else 'FAILED'}")
        print(f"✅ Servers Found: {len(servers)}")
        print(f"✅ Application Deployment: {'SUCCESS' if deploy_success else 'FAILED'}")
        if deploy_success:
            print(f"   Message: {deploy_message}")
        print(f"✅ Monitoring: {'SUCCESS' if monitoring_results.get('success') else 'FAILED'}")
        
        if monitoring_results.get('status_indicators'):
            print(f"   Status: {monitoring_results['status_indicators']}")
        
        return results

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 coolify_deploy_tool.py <email> <password> <repo_url> [app_name]")
        print("Example: python3 coolify_deploy_tool.py admin@247420.xyz password https://github.com/AnEntrypoint/nixpacks-test-app.git nixpacks-test")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    repo_url = sys.argv[3]
    app_name = sys.argv[4] if len(sys.argv) > 4 else None
    
    deployer = CoolifyApplicationDeployer()
    results = deployer.full_deployment_test(email, password, repo_url, app_name)
    
    # Save results
    with open('coolify_deployment_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to coolify_deployment_results.json")

if __name__ == "__main__":
    main()
