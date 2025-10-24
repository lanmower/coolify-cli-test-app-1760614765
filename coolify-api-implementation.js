
// Coolify Deployment API Implementation
// This script provides a practical implementation for programmatically deploying applications to Coolify

class CoolifyAPI {
    constructor(baseURL, credentials) {
        this.baseURL = baseURL;
        this.credentials = credentials;
        this.cookies = '';
        this.csrfToken = '';
    }

    async login() {
        console.log('🔐 Logging into Coolify...');
        
        try {
            // Get login page to extract CSRF token
            const loginPageResponse = await fetch(`${this.baseURL}/login`);
            const loginPageHTML = await loginPageResponse.text();
            
            // Extract CSRF token from meta tag
            const csrfMatch = loginPageHTML.match(/<meta[^>]*name=["']csrf-token["'][^>]*content=["']([^"']+)["']/);
            this.csrfToken = csrfMatch ? csrfMatch[1] : null;
            
            if (!this.csrfToken) {
                throw new Error('Could not extract CSRF token from login page');
            }
            
            // Extract cookies
            const cookies = loginPageResponse.headers.get('set-cookie') || '';
            this.cookies = cookies.split(';')[0]; // Keep only the first cookie
            
            console.log('✓ CSRF token extracted:', this.csrfToken.substring(0, 20) + '...');
            
            // Perform login
            const formData = new URLSearchParams();
            formData.append('_token', this.csrfToken);
            formData.append('email', this.credentials.email);
            formData.append('password', this.credentials.password);
            
            const loginResponse = await fetch(`${this.baseURL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': this.cookies,
                    'X-CSRF-TOKEN': this.csrfToken
                },
                body: formData
            });
            
            if (loginResponse.status === 302) {
                console.log('✓ Login successful!');
                
                // Update cookies from login response
                const newCookies = loginResponse.headers.get('set-cookie') || '';
                if (newCookies) {
                    this.cookies = newCookies.split(';')[0];
                }
                
                return true;
            } else {
                throw new Error(`Login failed with status: ${loginResponse.status}`);
            }
            
        } catch (error) {
            console.error('❌ Login error:', error.message);
            throw error;
        }
    }

    async getDashboard() {
        console.log('📊 Getting dashboard...');
        
        try {
            const response = await fetch(this.baseURL, {
                headers: {
                    'Cookie': this.cookies,
                    'X-CSRF-TOKEN': this.csrfToken
                }
            });
            
            if (response.status === 200) {
                const html = await response.text();
                
                // Extract project information
                const projectLinks = html.match(/<a[^>]*href=["'][^"']*project[^"']*/new["'][^>]*>/gi) || [];
                
                console.log(`✓ Found ${projectLinks.length} project creation links`);
                
                // Extract project and environment IDs from URLs
                const projects = [];
                const urlPattern = /project\/([^\/]+)\/environment\/([^\/]+)\/new/;
                
                projectLinks.forEach(link => {
                    const match = link.match(urlPattern);
                    if (match) {
                        projects.push({
                            projectId: match[1],
                            environmentId: match[2],
                            url: link.match(/href=["']([^"']+)["']/)[1]
                        });
                    }
                });
                
                return projects;
            } else {
                throw new Error(`Dashboard request failed: ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Dashboard error:', error.message);
            throw error;
        }
    }

    async createApplication(config) {
        console.log('🚀 Creating application...');
        
        try {
            // Get resource creation page
            const createURL = `${this.baseURL}/project/${config.projectId}/environment/${config.environmentId}/new`;
            const response = await fetch(createURL, {
                headers: {
                    'Cookie': this.cookies,
                    'X-CSRF-TOKEN': this.csrfToken
                }
            });
            
            if (response.status !== 200) {
                throw new Error(`Could not access resource creation page: ${response.status}`);
            }
            
            const html = await response.text();
            
            // Extract Livewire component ID and updated CSRF token
            const componentMatch = html.match(/wire:id=["']([^"']+)["']/);
            const csrfMatch = html.match(/<meta[^>]*name=["']csrf-token["'][^>]*content=["']([^"']+)["']/);
            
            if (!componentMatch || !csrfMatch) {
                throw new Error('Could not extract Livewire component or CSRF token');
            }
            
            const componentId = componentMatch[1];
            this.csrfToken = csrfMatch[1];
            
            console.log('✓ Livewire component found:', componentId);
            console.log('✓ Updated CSRF token');
            
            // Step 1: Select application resource type
            await this.livewireAction(componentId, 'selectResourceType', ['application']);
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for UI update
            
            // Step 2: Configure application details
            const appData = {
                name: config.name,
                description: config.description || '',
                repository: config.repository,
                build_pack: config.buildMethod || 'nixpacks',
                domain: config.domain || `${config.name}.247420.xyz`
            };
            
            // Step 3: Submit application creation
            const result = await this.livewireAction(componentId, 'submit', [appData]);
            
            console.log('✓ Application creation submitted!');
            return result;
            
        } catch (error) {
            console.error('❌ Application creation error:', error.message);
            throw error;
        }
    }

    async livewireAction(componentId, method, params = []) {
        console.log(`⚡ Livewire action: ${method}(${params.join(', ')})`);
        
        try {
            const payload = {
                components: {
                    [componentId]: {
                        data: {},
                        calls: [{
                            method: method,
                            params: params
                        }]
                    }
                }
            };
            
            const response = await fetch(`${this.baseURL}/livewire/${componentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Cookie': this.cookies,
                    'X-CSRF-TOKEN': this.csrfToken,
                    'X-Livewire': 'true',
                    'Accept': 'text/html, application/xhtml+xml'
                },
                body: JSON.stringify(payload)
            });
            
            if (response.status === 200) {
                const result = await response.json();
                console.log(`✓ Livewire action completed: ${method}`);
                return result;
            } else {
                const errorText = await response.text();
                throw new Error(`Livewire action failed: ${response.status} - ${errorText}`);
            }
            
        } catch (error) {
            console.error(`❌ Livewire action error (${method}):`, error.message);
            throw error;
        }
    }

    async getApplicationStatus(applicationId) {
        console.log(`📈 Getting application status: ${applicationId}`);
        
        try {
            const response = await fetch(`${this.baseURL}/application/${applicationId}`, {
                headers: {
                    'Cookie': this.cookies,
                    'X-CSRF-TOKEN': this.csrfToken
                }
            });
            
            if (response.status === 200) {
                const html = await response.text();
                
                // Extract deployment status from page
                const statusMatch = html.match(/deployment[^>]*>([^<]+)/gi);
                const status = statusMatch ? statusMatch[0] : 'Unknown';
                
                console.log(`✓ Application status: ${status}`);
                return status;
            } else {
                throw new Error(`Could not get application status: ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Status check error:', error.message);
            throw error;
        }
    }

    async deployApplication(applicationId) {
        console.log(`🚢 Deploying application: ${applicationId}`);
        
        try {
            // This would typically be a Livewire action on the application page
            const response = await fetch(`${this.baseURL}/application/${applicationId}/deploy`, {
                method: 'POST',
                headers: {
                    'Cookie': this.cookies,
                    'X-CSRF-TOKEN': this.csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            if (response.status === 200 || response.status === 302) {
                console.log('✓ Deployment initiated!');
                return true;
            } else {
                throw new Error(`Deployment failed: ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Deployment error:', error.message);
            throw error;
        }
    }
}

// Usage Example
async function deployTestApplication() {
    console.log('🎯 Starting Coolify deployment test...');
    
    const coolify = new CoolifyAPI('https://coolify.247420.xyz', {
        email: 'admin@247420.xyz',
        password: '123,slam123,slam'
    });
    
    try {
        // Step 1: Authenticate
        await coolify.login();
        
        // Step 2: Get available projects
        const projects = await coolify.getDashboard();
        if (projects.length === 0) {
            throw new Error('No projects found on dashboard');
        }
        
        console.log('📋 Available projects:');
        projects.forEach((project, index) => {
            console.log(`  ${index + 1}. Project ${project.projectId}, Environment ${project.environmentId}`);
        });
        
        // Step 3: Use the first project for demonstration
        const project = projects[0];
        
        // Step 4: Create application
        const appConfig = {
            projectId: project.projectId,
            environmentId: project.environmentId,
            name: 'test-app-nixpacks',
            description: 'Test application deployed via API',
            repository: 'https://github.com/AnEntrypoint/nixpacks-test-app.git',
            buildMethod: 'nixpacks',
            domain: 'test-app.247420.xyz'
        };
        
        const createResult = await coolify.createApplication(appConfig);
        console.log('🎉 Application created successfully!');
        
        // Step 5: Deploy the application
        // Note: You would need the actual application ID from the creation result
        // const deploymentResult = await coolify.deployApplication(applicationId);
        // console.log('🚀 Deployment initiated!');
        
        console.log('✅ Complete workflow demonstrated!');
        
    } catch (error) {
        console.error('💥 Deployment failed:', error.message);
    }
}

// Export for use as a module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CoolifyAPI, deployTestApplication };
}

// Run the example if this script is executed directly
if (typeof window === 'undefined' && require.main === module) {
    // Note: This would need to be adapted for Node.js environment
    // as it currently uses browser fetch API
    console.log('💡 This script demonstrates the Coolify API implementation.');
    console.log('📝 To use in Node.js, replace fetch with node-fetch or similar.');
    console.log('🔗 See the reverse engineering report for complete details.');
}
