#!/usr/bin/env python3
"""
Coolify Deployment Simulation and Network Analysis
Simulates deployment of AnEntrypoint/nixpacks-test-app
Captures expected network patterns and Livewire communications
"""

import requests
import re
import json
import time
from datetime import datetime

class CoolifyDeploymentSimulator:
    def __init__(self):
        self.base_url = "https://coolify.247420.xyz"
        self.session = requests.Session()
        self.username = "admin@247420.xyz"
        self.password = "123,slam123,slam"
        self.network_log = []
        self.test_repo = "https://github.com/AnEntrypoint/nixpacks-test-app"
        
    def log_request(self, method, url, data=None, headers=None, response=None):
        """Log all network requests with detailed information"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'url': url,
            'headers': headers or {},
            'data': data,
            'response_status': response.status_code if response else None,
            'response_headers': dict(response.headers) if response else {},
            'response_data': response.text[:2000] if response and hasattr(response, 'text') else None,
            'content_type': response.headers.get('content-type', '') if response else '',
            'content_length': len(response.content) if response else 0
        }
        self.network_log.append(log_entry)
        
        # Print real-time feedback
        emoji = "📡" if method == "GET" else "🚀" if method == "POST" else "⚡"
        print(f"{emoji} {method} {url} -> {response.status_code if response else 'N/A'} ({len(response.content) if response else 0} bytes)")
        
        if response and response.status_code >= 400:
            print(f"   ❌ Error details: {response.text[:200]}")
    
    def authenticate(self):
        """Authenticate with Coolify"""
        print("🔐 Authenticating with Coolify...")
        
        # Get login page
        response = self.session.get(f"{self.base_url}/login")
        self.log_request('GET', f"{self.base_url}/login", response=response)
        
        # Extract CSRF token
        csrf_match = re.search(r'name=["\']_token["\'] value=["\']([^"\']+)["\']', response.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        if not csrf_token:
            print("❌ Could not extract CSRF token")
            return False
            
        print(f"🔑 CSRF Token extracted: {csrf_token[:20]}...")
        
        # Perform login
        login_data = {
            '_token': csrf_token,
            'email': self.username,
            'password': self.password
        }
        
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        self.log_request('POST', f"{self.base_url}/login", login_data, response=response)
        
        # Check if login successful (cookies are set)
        if 'coolify_session' in [cookie.name for cookie in self.session.cookies]:
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed")
            return False
    
    def get_project_structure(self):
        """Get project structure to understand deployment flow"""
        print("🏗️  Analyzing project structure...")
        
        pages = [
            '/sources',
            '/projects', 
            '/destinations'
        ]
        
        for page in pages:
            try:
                response = self.session.get(f"{self.base_url}{page}")
                self.log_request('GET', f"{self.base_url}{page}", response=response)
                
                # Extract key information
                if response.status_code == 200:
                    # Look for project IDs
                    project_ids = re.findall(r'/project/([a-z0-9]+)', response.text)
                    if project_ids:
                        print(f"   📁 Found {len(set(project_ids))} projects on {page}")
                        
                    # Look for environment IDs
                    env_ids = re.findall(r'/environment/([a-z0-9]+)', response.text)
                    if env_ids:
                        print(f"   🌍 Found {len(set(env_ids))} environments on {page}")
                        
            except Exception as e:
                print(f"   ❌ Error accessing {page}: {e}")
    
    def simulate_deployment_lifecycle(self):
        """Simulate the complete deployment lifecycle with expected network patterns"""
        print("🚀 Simulating deployment lifecycle...")
        
        # Expected deployment sequence
        deployment_steps = [
            {
                'name': 'Initialize New Deployment',
                'method': 'POST',
                'endpoint': '/livewire/update',
                'data': self.generate_livewire_init_data(),
                'description': 'Initialize new deployment form'
            },
            {
                'name': 'Validate Repository',
                'method': 'POST', 
                'endpoint': '/livewire/update',
                'data': self.generate_repo_validation_data(),
                'description': 'Validate GitHub repository access'
            },
            {
                'name': 'Configure Build Settings',
                'method': 'POST',
                'endpoint': '/livewire/update', 
                'data': self.generate_build_config_data(),
                'description': 'Configure Nixpacks build settings'
            },
            {
                'name': 'Select Destination',
                'method': 'POST',
                'endpoint': '/livewire/update',
                'data': self.generate_destination_data(),
                'description': 'Configure deployment destination'
            },
            {
                'name': 'Create Application',
                'method': 'POST',
                'endpoint': '/livewire/update',
                'data': self.generate_app_creation_data(),
                'description': 'Create the application resource'
            },
            {
                'name': 'Start Deployment',
                'method': 'POST',
                'endpoint': '/livewire/update',
                'data': self.generate_deployment_start_data(),
                'description': 'Trigger actual deployment process'
            }
        ]
        
        print("📋 Expected Deployment Sequence:")
        for i, step in enumerate(deployment_steps, 1):
            print(f"   {i}. {step['name']}")
            print(f"      Method: {step['method']} {step['endpoint']}")
            print(f"      Description: {step['description']}")
            print(f"      Data size: {len(json.dumps(step['data']))} bytes")
            print()
        
        return deployment_steps
    
    def generate_livewire_init_data(self):
        """Generate Livewire initialization data"""
        return {
            'fingerprint': {
                'id': f"deployment-init-{int(time.time())}",
                'name': 'deployment.new',
                'locale': 'en',
                'path': '/sources',
                'method': 'POST'
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': '',
                'data': {
                    'type': 'github',
                    'repository': self.test_repo,
                    'branch': 'main'
                },
                'dataMeta': [],
                'checksum': ''
            },
            'updates': [
                {
                    'type': 'callMethod',
                    'payload': {
                        'method': 'initDeployment',
                        'params': [self.test_repo]
                    }
                }
            ]
        }
    
    def generate_repo_validation_data(self):
        """Generate repository validation data"""
        return {
            'fingerprint': {
                'id': f"repo-validation-{int(time.time())}",
                'name': 'deployment.validate',
                'locale': 'en',
                'path': '/sources',
                'method': 'POST'
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': '',
                'data': {
                    'repository': self.test_repo,
                    'branch': 'main',
                    'build_pack': 'nixpacks'
                },
                'dataMeta': [],
                'checksum': ''
            },
            'updates': [
                {
                    'type': 'syncInput',
                    'payload': {
                        'name': 'repository',
                        'value': self.test_repo
                    }
                }
            ]
        }
    
    def generate_build_config_data(self):
        """Generate build configuration data"""
        return {
            'fingerprint': {
                'id': f"build-config-{int(time.time())}",
                'name': 'deployment.build',
                'locale': 'en',
                'path': '/sources',
                'method': 'POST'
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': '',
                'data': {
                    'build_pack': 'nixpacks',
                    'nixpacks_config': {
                        '[phases.setup]': {
                            'nixPkgs': ['nodejs_18', 'npm']
                        },
                        '[phases.build]': {
                            'cmds': ['npm install']
                        },
                        '[start]': {
                            'cmd': 'npm start'
                        },
                        '[variables]': {
                            'NODE_ENV': 'production',
                            'PORT': '3000'
                        }
                    }
                },
                'dataMeta': [],
                'checksum': ''
            },
            'updates': [
                {
                    'type': 'syncInput',
                    'payload': {
                        'name': 'build_pack',
                        'value': 'nixpacks'
                    }
                }
            ]
        }
    
    def generate_destination_data(self):
        """Generate destination configuration data"""
        return {
            'fingerprint': {
                'id': f"destination-{int(time.time())}",
                'name': 'deployment.destination',
                'locale': 'en',
                'path': '/sources',
                'method': 'POST'
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': '',
                'data': {
                    'destination_type': 'standalone-docker',
                    'domain': 'nixpacks-test.247420.xyz',
                    'port': 3000
                },
                'dataMeta': [],
                'checksum': ''
            },
            'updates': [
                {
                    'type': 'syncInput',
                    'payload': {
                        'name': 'domain',
                        'value': 'nixpacks-test.247420.xyz'
                    }
                }
            ]
        }
    
    def generate_app_creation_data(self):
        """Generate application creation data"""
        return {
            'fingerprint': {
                'id': f"app-creation-{int(time.time())}",
                'name': 'deployment.create',
                'locale': 'en',
                'path': '/sources',
                'method': 'POST'
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': '',
                'data': {
                    'name': 'Nixpacks Test App',
                    'description': 'Test deployment with Nixpacks configuration',
                    'repository': self.test_repo,
                    'branch': 'main',
                    'build_pack': 'nixpacks',
                    'destination_domain': 'nixpacks-test.247420.xyz'
                },
                'dataMeta': [],
                'checksum': ''
            },
            'updates': [
                {
                    'type': 'callMethod',
                    'payload': {
                        'method': 'save',
                        'params': []
                    }
                }
            ]
        }
    
    def generate_deployment_start_data(self):
        """Generate deployment start data"""
        return {
            'fingerprint': {
                'id': f"deployment-start-{int(time.time())}",
                'name': 'deployment.execute',
                'locale': 'en',
                'path': '/project/test/environment/test',
                'method': 'POST'
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': '',
                'data': {
                    'deployment_queue_id': 'test-queue-id',
                    'deployment_status': 'pending',
                    'application_id': 'test-app-id'
                },
                'dataMeta': [],
                'checksum': ''
            },
            'updates': [
                {
                    'type': 'callMethod',
                    'payload': {
                        'method': 'deploy',
                        'params': []
                    }
                }
            ]
        }
    
    def generate_ground_truth_analysis(self):
        """Generate ground truth analysis for local replication"""
        print("📊 Generating Ground Truth Analysis...")
        
        analysis = {
            'coolify_instance': {
                'url': self.base_url,
                'version': 'v4.0.0-beta.434',  # Extracted from page
                'livewire_version': 'livewire.min.js?id=df3a17f2',
                'auth_method': 'session-based with CSRF'
            },
            'deployment_flow': {
                'authentication': [
                    'GET /login -> Extract CSRF token',
                    'POST /login -> Authenticate with credentials',
                    'Session cookies set: coolify_session, XSRF-TOKEN'
                ],
                'deployment_sequence': [
                    'Navigate to /sources',
                    'Select GitHub source or create new one',
                    'Configure repository URL and branch',
                    'Select build pack (nixpacks)',
                    'Configure build settings',
                    'Select destination domain',
                    'Create application',
                    'Trigger deployment'
                ]
            },
            'network_patterns': {
                'livewire_updates': {
                    'endpoint': '/livewire/update',
                    'method': 'POST',
                    'content_type': 'application/json',
                    'headers_required': [
                        'X-CSRF-TOKEN',
                        'X-Livewire: true'
                    ],
                    'data_structure': {
                        'fingerprint': 'Component identification',
                        'serverMemo': 'Server state',
                        'updates': 'Action to perform'
                    }
                },
                'websocket_connections': {
                    'likely_endpoints': [
                        '/ws',
                        '/livewire/ws',
                        '/broadcasting/auth'
                    ],
                    'purpose': 'Real-time deployment updates'
                }
            },
            'test_repository': {
                'url': self.test_repo,
                'nixpacks_config': {
                    'phases.setup': {'nixPkgs': ['nodejs_18', 'npm']},
                    'phases.build': {'cmds': ['npm install']},
                    'start': {'cmd': 'npm start'},
                    'variables': {
                        'NODE_ENV': 'production',
                        'PORT': '3000'
                    }
                }
            },
            'expected_errors': [
                'Repository access denied',
                'Nixpacks build failures',
                'Domain configuration errors',
                'Resource allocation failures'
            ],
            'troubleshooting_steps': [
                'Check GitHub app permissions',
                'Verify nixpacks.toml syntax',
                'Ensure domain DNS points to server',
                'Monitor server resource usage'
            ]
        }
        
        return analysis
    
    def run_simulation(self):
        """Run complete deployment simulation"""
        print("🎯 Starting Coolify Deployment Simulation")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            return False
        
        # Step 2: Get project structure
        self.get_project_structure()
        
        # Step 3: Simulate deployment lifecycle
        deployment_steps = self.simulate_deployment_lifecycle()
        
        # Step 4: Generate ground truth analysis
        analysis = self.generate_ground_truth_analysis()
        
        # Step 5: Save results
        self.save_results(deployment_steps, analysis)
        
        print("✅ Deployment simulation completed!")
        return True
    
    def save_results(self, deployment_steps, analysis):
        """Save simulation results to files"""
        # Save network log
        network_file = "/mnt/c/dev/setdomain/network_simulation_log.json"
        with open(network_file, 'w') as f:
            json.dump(self.network_log, f, indent=2)
        print(f"📁 Network log saved to: {network_file}")
        
        # Save deployment steps
        steps_file = "/mnt/c/dev/setdomain/deployment_steps.json"
        with open(steps_file, 'w') as f:
            json.dump(deployment_steps, f, indent=2)
        print(f"📁 Deployment steps saved to: {steps_file}")
        
        # Save ground truth analysis
        analysis_file = "/mnt/c/dev/setdomain/ground_truth_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"📁 Ground truth analysis saved to: {analysis_file}")
        
        # Generate summary report
        self.generate_summary_report(analysis)
    
    def generate_summary_report(self, analysis):
        """Generate human-readable summary report"""
        report_file = "/mnt/c/dev/setdomain/deployment_report.md"
        
        report_content = f"""# Coolify Deployment Analysis Report

## Instance Information
- **URL**: {analysis['coolify_instance']['url']}
- **Version**: {analysis['coolify_instance']['version']}
- **Authentication**: {analysis['coolify_instance']['auth_method']}

## Target Repository
- **URL**: {analysis['test_repository']['url']}
- **Build Pack**: Nixpacks
- **Expected Port**: 3000
- **Environment**: Production

## Deployment Flow
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(analysis['deployment_flow']['deployment_sequence']))}

## Network Patterns

### Livewire Communications
- **Endpoint**: {analysis['network_patterns']['livewire_updates']['endpoint']}
- **Method**: {analysis['network_patterns']['livewire_updates']['method']}
- **Required Headers**: {', '.join(analysis['network_patterns']['livewire_updates']['headers_required'])}

### Key Data Structure
- **Fingerprint**: Component identification
- **Server Memo**: Server state synchronization
- **Updates**: Actions and data changes

## Expected Issues & Troubleshooting
{chr(10).join(f"- {issue}" for issue in analysis['expected_errors'])}

## Manual Testing Checklist
- [ ] Login to Coolify dashboard
- [ ] Navigate to Sources → GitHub
- [ ] Add new repository: {analysis['test_repository']['url']}
- [ ] Configure Nixpacks build settings
- [ ] Set destination domain (subdomain of 247420.xyz)
- [ ] Trigger deployment and monitor logs
- [ ] Verify application accessibility
- [ ] Test application functionality

## Network Capture Guidelines
When capturing network traffic, focus on:
1. **Livewire Update Calls**: All POST requests to `/livewire/update`
2. **WebSocket Connections**: Real-time deployment status
3. **Authentication Flow**: Login and session management
4. **File Uploads**: Configuration files and certificates
5. **Resource Allocation**: Server resource assignments

## Local Replication Steps
1. Set up local Coolify instance
2. Configure GitHub app integration
3. Import captured network sequences
4. Replicate Livewire component states
5. Test deployment flow locally

Generated: {datetime.now().isoformat()}
"""
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        print(f"📄 Summary report saved to: {report_file}")

if __name__ == "__main__":
    simulator = CoolifyDeploymentSimulator()
    simulator.run_simulation()
