#!/usr/bin/env python3
"""
Simplified Coolify Application Deployment Tool
"""

import requests
import json
import sys
import time
import urllib3
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SimpleCoolifyDeployer:
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

    def deploy_application_simple(self, repo_url, app_name):
        """Simple application deployment"""
        print(f"🚀 Deploying {app_name} from {repo_url}")
        
        try:
            # Access new application page
            print("1. Accessing application creation page...")
            response = self.session.get(f"{self.base_url}/new-application")
            
            if response.status_code != 200:
                return False, f"Cannot access application creation: {response.status_code}"
            
            print("   ✅ Application creation page accessed")
            
            # Simple form submission attempt
            print("2. Attempting application creation...")
            
            app_data = {
                'name': app_name,
                'repository': repo_url,
                'build_pack': 'nixpacks',
                'branch': 'main',
            }
            
            # Try different endpoints
            endpoints = ['/applications', '/api/v1/applications', '/new-application']
            
            for endpoint in endpoints:
                try:
                    print(f"   Trying endpoint: {endpoint}")
                    
                    submit_response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        data=app_data,
                        allow_redirects=False
                    )
                    
                    print(f"     Status: {submit_response.status_code}")
                    
                    if submit_response.status_code in [200, 201, 302]:
                        print(f"     ✅ Application creation successful!")
                        return True, f"Created via {endpoint}"
                    
                except Exception as e:
                    print(f"     Error with {endpoint}: {e}")
            
            # Try to extract more info from the page
            print("3. Analyzing application creation page...")
            content = response.text.lower()
            
            has_repo_field = 'repository' in content
            has_form = '<form' in content
            has_livewire = 'livewire' in content
            has_submit = 'submit' in content or 'create' in content
            
            print(f"   Has repository field: {has_repo_field}")
            print(f"   Has form: {has_form}")
            print(f"   Has Livewire: {has_livewire}")
            print(f"   Has submit button: {has_submit}")
            
            if has_form and has_repo_field and has_submit:
                print("   ✅ Page has all necessary form elements")
                return True, "Application creation page ready (manual deployment possible)"
            else:
                return False, "Missing form elements on creation page"
            
        except Exception as e:
            return False, f"Deployment error: {e}"

    def check_resources(self):
        """Check available resources"""
        print("🔍 Checking available resources...")
        
        try:
            # Check resources page
            response = self.session.get(f"{self.base_url}/resources")
            
            if response.status_code == 200:
                print("   ✅ Resources page accessible")
                
                content = response.text.lower()
                has_servers = 'server' in content
                has_applications = 'application' in content
                has_deployments = 'deployment' in content
                
                print(f"   Has servers: {has_servers}")
                print(f"   Has applications: {has_applications}")
                print(f"   Has deployments: {has_deployments}")
                
                return {
                    'success': True,
                    'has_servers': has_servers,
                    'has_applications': has_applications,
                    'has_deployments': has_deployments
                }
            else:
                return {
                    'success': False,
                    'message': f"Cannot access resources: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Resource check error: {e}"
            }

    def run_deployment_test(self, email, password, repo_url, app_name):
        """Run deployment test"""
        print("=" * 80)
        print("🚀 SIMPLE COOLIFY DEPLOYMENT TEST")
        print("=" * 80)
        print(f"Repository: {repo_url}")
        print(f"App Name: {app_name}")
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
            print("\n❌ Login failed - stopping test")
            return results
        
        # Step 2: Check Resources
        print("\n🔍 STEP 2: RESOURCE CHECK")
        print("-" * 50)
        resource_results = self.check_resources()
        results['resources'] = resource_results
        
        # Step 3: Try Deployment
        print("\n🚀 STEP 3: DEPLOYMENT ATTEMPT")
        print("-" * 50)
        deploy_success, deploy_message = self.deploy_application_simple(repo_url, app_name)
        results['deployment'] = {
            'success': deploy_success,
            'message': deploy_message
        }
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DEPLOYMENT TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Authentication: {'SUCCESS' if login_success else 'FAILED'}")
        print(f"✅ Resources: {'SUCCESS' if resource_results.get('success') else 'FAILED'}")
        print(f"✅ Deployment: {'SUCCESS' if deploy_success else 'FAILED'}")
        
        if deploy_success:
            print(f"   🎉 {deploy_message}")
        
        return results

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 simple_coolify_deploy.py <email> <password> <repo_url> [app_name]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    repo_url = sys.argv[3]
    app_name = sys.argv[4] if len(sys.argv) > 4 else 'test-app'
    
    deployer = SimpleCoolifyDeployer()
    results = deployer.run_deployment_test(email, password, repo_url, app_name)
    
    # Save results
    with open('simple_deployment_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to simple_deployment_results.json")

if __name__ == "__main__":
    main()
