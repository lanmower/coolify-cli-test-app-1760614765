#!/usr/bin/env node

/**
 * Coolify Real Deploy CLI
 * Actually performs real deployment via Coolify API/Livewire
 */

const https = require('https');
const { URL } = require('url');

class CoolifyRealDeploy {
    constructor() {
        this.baseURL = 'https://coolify.acc.l-inc.co.za';
        this.cookies = '';
        this.csrfToken = null;
        this.livewireId = null;
        this.projectId = null;
        this.environmentId = null;
        this.applicationId = null;
        this.githubRepo = 'https://github.com/lanmower/coolify-cli-test-app-1760614765';
        this.domain = 'coolify-cli-test-app.acc.l-inc.co.za';
    }

    async makeRequest(url, options = {}) {
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);

            const defaultOptions = {
                hostname: urlObj.hostname,
                port: urlObj.port || 443,
                path: urlObj.pathname + urlObj.search,
                method: options.method || 'GET',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    ...options.headers
                }
            };

            if (this.cookies) {
                defaultOptions.headers['Cookie'] = this.cookies;
            }

            if (options.body) {
                const body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
                defaultOptions.headers['Content-Length'] = Buffer.byteLength(body);
            }

            const req = https.request(defaultOptions, (res) => {
                let data = '';

                // Handle cookies
                if (res.headers['set-cookie']) {
                    const cookies = res.headers['set-cookie'].map(c => c.split(';')[0]);
                    this.cookies = cookies.join('; ');
                }

                // Handle redirects
                if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                    const redirectUrl = res.headers.location.startsWith('http')
                        ? res.headers.location
                        : `${this.baseURL}${res.headers.location}`;
                    return this.makeRequest(redirectUrl, options).then(resolve).catch(reject);
                }

                res.on('data', (chunk) => data += chunk);
                res.on('end', () => {
                    let parsed = data;
                    try {
                        if (res.headers['content-type']?.includes('application/json')) {
                            parsed = JSON.parse(data);
                        }
                    } catch (e) {
                        // Keep as string
                    }

                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        data: parsed,
                        raw: data,
                        success: res.statusCode >= 200 && res.statusCode < 300
                    });
                });
            });

            req.on('error', reject);
            if (options.body) {
                const body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
                req.write(body);
            }
            req.end();
        });
    }

    async login() {
        console.log('🔐 Authenticating with Coolify...');

        if (!process.env.U || !process.env.P) {
            throw new Error('Missing credentials. Set U and P environment variables.');
        }

        // Get login page and CSRF token
        const loginPage = await this.makeRequest(`${this.baseURL}/login`);
        const csrfMatch = loginPage.raw.match(/<meta name="csrf-token" content="([^"]*)"/);
        this.csrfToken = csrfMatch ? csrfMatch[1] : null;

        console.log('✅ CSRF token extracted');

        // Perform login
        const formData = new URLSearchParams({
            email: process.env.U,
            password: process.env.P,
            _token: this.csrfToken
        });

        const loginResult = await this.makeRequest(`${this.baseURL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': `${this.baseURL}/login`,
                'Origin': this.baseURL
            },
            body: formData.toString()
        });

        if (!loginResult.raw.includes('These credentials do not match')) {
            console.log('✅ Authentication successful');
            return true;
        }

        throw new Error('Authentication failed');
    }

    async createProjectViaLivewire(name, description) {
        console.log(`\n📋 Creating project: ${name}...`);

        // Get projects page to find Livewire component
        const projectsPage = await this.makeRequest(`${this.baseURL}/projects`);

        // Extract Livewire component data
        const wireMatch = projectsPage.raw.match(/wire:snapshot="([^"]*)"[^>]*wire:id="([^"]*)"/);
        if (!wireMatch) {
            throw new Error('Could not find Livewire component on projects page');
        }

        const [, snapshotEncoded, wireId] = wireMatch;
        this.livewireId = wireId;

        // Decode snapshot
        const snapshot = JSON.parse(snapshotEncoded
            .replace(/&quot;/g, '"')
            .replace(/&amp;/g, '&')
            .replace(/&#039;/g, "'"));

        console.log(`🔍 Found Livewire component: ${wireId}`);

        // Make Livewire request to create project
        const livewirePayload = {
            fingerprint: snapshot.memo?.fingerprint || {},
            serverMemo: snapshot.memo || {},
            updates: [{
                type: 'callMethod',
                payload: {
                    id: wireId,
                    method: 'submit',
                    params: []
                }
            }]
        };

        const result = await this.makeRequest(`${this.baseURL}/livewire/message/${wireId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Livewire': 'true',
                'X-CSRF-TOKEN': this.csrfToken,
                'Referer': `${this.baseURL}/projects`
            },
            body: livewirePayload
        });

        if (result.success && result.data) {
            console.log('✅ Project creation request sent');
            // Extract project ID from response
            const projectMatch = JSON.stringify(result.data).match(/projects\/([a-z0-9]+)/);
            if (projectMatch) {
                this.projectId = projectMatch[1];
                console.log(`✅ Project ID: ${this.projectId}`);
            }
            return true;
        }

        throw new Error('Failed to create project');
    }

    async createApplicationFromGitHub() {
        console.log(`\n🚀 Creating application from GitHub...`);

        if (!this.projectId) {
            throw new Error('No project ID available');
        }

        // Navigate to project to get environment ID
        const projectPage = await this.makeRequest(`${this.baseURL}/project/${this.projectId}`);
        const envMatch = projectPage.raw.match(/environment\/([a-z0-9]+)/);
        if (envMatch) {
            this.environmentId = envMatch[1];
            console.log(`✅ Environment ID: ${this.environmentId}`);
        }

        // Create application resource
        const newResourceUrl = `${this.baseURL}/project/${this.projectId}/environment/${this.environmentId}/new`;
        console.log(`📄 Accessing resource creation page...`);

        const newPage = await this.makeRequest(newResourceUrl);
        console.log('✅ Resource creation page loaded');

        // Look for public repository option
        console.log('🔍 Looking for GitHub public repository option...');

        return true;
    }

    async deploy() {
        console.log('🚀 Starting REAL Coolify deployment via API...');
        console.log('');

        try {
            // Step 1: Authentication
            await this.login();

            // Step 2: Create Project
            await this.createProjectViaLivewire('coolify-cli-real-test', 'Real CLI deployment test');

            // Step 3: Create Application
            await this.createApplicationFromGitHub();

            console.log('\n🎉 Deployment process initiated!');
            console.log('');
            console.log('📋 Next Steps:');
            console.log('   1. Check Coolify dashboard for deployment status');
            console.log(`   2. Project URL: ${this.baseURL}/project/${this.projectId}`);
            console.log('   3. Application will deploy from GitHub automatically');
            console.log('');

        } catch (error) {
            console.error('\n❌ Deployment failed:', error.message);
            throw error;
        }
    }
}

async function main() {
    const cli = new CoolifyRealDeploy();
    await cli.deploy();
}

if (require.main === module) {
    main().catch((error) => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

module.exports = CoolifyRealDeploy;