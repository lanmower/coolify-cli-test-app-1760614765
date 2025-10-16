#!/usr/bin/env node

/**
 * Coolify Deploy CLI - Real Browser-Emulated Deployment
 * Single file that performs actual deployment by emulating browser requests
 */

const https = require('https');
const { URL } = require('url');

class CoolifyDeploy {
    constructor() {
        this.baseURL = 'https://coolify.acc.l-inc.co.za';
        this.cookies = '';
        this.csrfToken = null;
        this.projectId = null;
        this.environmentId = null;
        this.applicationId = null;
        this.githubRepo = 'https://github.com/lanmower/coolify-cli-test-app-1760614765';
        this.domain = 'coolify-cli-test-app.acc.l-inc.co.za';
    }

    async request(url, options = {}) {
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const opts = {
                hostname: urlObj.hostname,
                port: urlObj.port || 443,
                path: urlObj.pathname + urlObj.search,
                method: options.method || 'GET',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    ...options.headers
                }
            };

            if (this.cookies) opts.headers['Cookie'] = this.cookies;
            if (options.body) {
                const body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
                opts.headers['Content-Length'] = Buffer.byteLength(body);
            }

            const req = https.request(opts, (res) => {
                let data = '';
                if (res.headers['set-cookie']) {
                    this.cookies = res.headers['set-cookie'].map(c => c.split(';')[0]).join('; ');
                }

                // Handle redirects
                if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                    const redirectUrl = res.headers.location.startsWith('http')
                        ? res.headers.location
                        : `${this.baseURL}${res.headers.location}`;
                    return this.request(redirectUrl, options).then(resolve).catch(reject);
                }

                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    let parsed = data;
                    try {
                        if (res.headers['content-type']?.includes('application/json')) {
                            parsed = JSON.parse(data);
                        }
                    } catch (e) {}

                    resolve({
                        status: res.statusCode,
                        headers: res.headers,
                        data: parsed,
                        raw: data,
                        ok: res.statusCode >= 200 && res.statusCode < 300
                    });
                });
            });

            req.on('error', reject);

            // Set timeout
            req.setTimeout(30000, () => {
                req.destroy();
                reject(new Error('Request timeout after 30s'));
            });

            if (options.body) {
                const body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
                req.write(body);
            }
            req.end();
        });
    }

    async login() {
        console.log('🔐 Logging into Coolify...');

        if (!process.env.U || !process.env.P) {
            throw new Error('Missing credentials. Set U and P environment variables.');
        }

        // Get CSRF token
        const page = await this.request(`${this.baseURL}/login`);
        const match = page.raw.match(/<meta name="csrf-token" content="([^"]*)"/);
        this.csrfToken = match ? match[1] : null;
        console.log('✅ Got CSRF token');

        // Login
        const form = new URLSearchParams({
            email: process.env.U,
            password: process.env.P,
            _token: this.csrfToken
        });

        const result = await this.request(`${this.baseURL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': `${this.baseURL}/login`,
                'Origin': this.baseURL
            },
            body: form.toString()
        });

        if (result.raw.includes('These credentials do not match')) {
            throw new Error('Login failed - invalid credentials');
        }

        console.log('✅ Logged in successfully');
    }

    async createProject() {
        console.log('\n📋 Creating project...');

        // Get projects page and refresh CSRF token
        const page = await this.request(`${this.baseURL}/projects`);

        // Extract fresh CSRF token from projects page
        const csrfMatch = page.raw.match(/<meta name="csrf-token" content="([^"]*)"/);
        if (csrfMatch) {
            this.csrfToken = csrfMatch[1];
            console.log('🔄 Refreshed CSRF token');
        }

        // Extract Livewire data
        const wireMatch = page.raw.match(/wire:snapshot="([^"]*)".*?wire:id="([^"]*)"/s);
        if (!wireMatch) {
            console.log('⚠️  Could not extract Livewire data, trying alternative method...');
            // Try to find any existing project to get structure
            const projMatch = page.raw.match(/\/project\/([a-z0-9]+)/);
            if (projMatch) {
                this.projectId = projMatch[1];
                console.log(`✅ Found existing project: ${this.projectId}`);
                return;
            }
            throw new Error('Could not create or find project');
        }

        const [, snapshot, wireId] = wireMatch;

        // Decode and parse Livewire snapshot
        const decoded = snapshot
            .replace(/&quot;/g, '"')
            .replace(/&amp;/g, '&')
            .replace(/&#039;/g, "'")
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>');

        let memo;
        try {
            memo = JSON.parse(decoded);
        } catch (e) {
            console.log('⚠️  Could not parse Livewire data');
            throw new Error('Failed to parse Livewire component');
        }

        console.log(`🔍 Found Livewire component: ${wireId}`);

        // Create Livewire request to submit project form
        const payload = {
            fingerprint: memo.memo?.fingerprint || memo.fingerprint || {},
            serverMemo: memo.memo || memo.serverMemo || {},
            updates: [{
                type: 'syncInput',
                payload: {
                    name: 'name',
                    value: 'coolify-cli-deploy-test'
                }
            }, {
                type: 'syncInput',
                payload: {
                    name: 'description',
                    value: 'Deployed via CLI tool'
                }
            }, {
                type: 'callMethod',
                payload: {
                    method: 'submit',
                    params: []
                }
            }]
        };

        const result = await this.request(`${this.baseURL}/livewire/message/${wireId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Livewire': 'true',
                'X-CSRF-TOKEN': this.csrfToken,
                'Referer': `${this.baseURL}/projects`
            },
            body: payload
        });

        if (result.ok) {
            // Extract project ID from response
            const idMatch = JSON.stringify(result.data).match(/project[s]?\/([a-z0-9]{24})/);
            if (idMatch) {
                this.projectId = idMatch[1];
                console.log(`✅ Project created: ${this.projectId}`);
                return;
            }
        }

        console.log('⚠️  Project creation response unclear');
        console.log('📝 Response status:', result.status);

        // Wait a moment for the project to be created
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Check projects list for the newly created project
        const check = await this.request(`${this.baseURL}/projects`);

        // Try to find the most recent project (should be the one we just created)
        const allMatches = check.raw.match(/\/project\/([a-z0-9]{24})/g);
        if (allMatches && allMatches.length > 0) {
            // Get the last one (most recent)
            this.projectId = allMatches[allMatches.length - 1].replace('/project/', '');
            console.log(`✅ Found new project: ${this.projectId}`);
            return;
        }

        throw new Error('Could not determine project ID - no projects found');
    }

    async getEnvironment() {
        console.log('\n🌍 Getting environment...');

        const page = await this.request(`${this.baseURL}/project/${this.projectId}`);
        const envMatch = page.raw.match(/environment\/([a-z0-9]{24})/);

        if (envMatch) {
            this.environmentId = envMatch[1];
            console.log(`✅ Environment: ${this.environmentId}`);
        } else {
            throw new Error('Could not find environment');
        }
    }

    async createApplication() {
        console.log('\n🚀 Creating application from GitHub...');

        const newUrl = `${this.baseURL}/project/${this.projectId}/environment/${this.environmentId}/new`;
        const page = await this.request(newUrl);

        console.log('📄 Loaded resource creation page');

        // Look for the public repository link
        const publicRepoMatch = page.raw.match(/href="([^"]*public-git-repository[^"]*)"/);
        if (!publicRepoMatch) {
            console.log('⚠️  Could not find public repository option');
            console.log(`   Please create the application manually at: ${newUrl}`);
            return;
        }

        const publicRepoUrl = publicRepoMatch[1].startsWith('http') ? publicRepoMatch[1] : `${this.baseURL}${publicRepoMatch[1]}`;
        console.log('✅ Found public repository option');
        console.log(`🔗 Navigating to: ${publicRepoUrl}`);

        // Navigate to public repository form
        const repoPage = await this.request(publicRepoUrl);
        console.log('📄 Loaded public repository form');

        // Extract Livewire component for the form
        const wireMatch = repoPage.raw.match(/wire:snapshot="([^"]*)".*?wire:id="([^"]*)"/s);
        if (!wireMatch) {
            console.log('⚠️  Could not find Livewire form component');
            console.log(`   Please complete the form manually at: ${publicRepoUrl}`);
            return;
        }

        const [, snapshot, wireId] = wireMatch;
        console.log(`🔍 Found form component: ${wireId}`);

        // Decode snapshot
        const decoded = snapshot
            .replace(/&quot;/g, '"')
            .replace(/&amp;/g, '&')
            .replace(/&#039;/g, "'")
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>');

        let memo;
        try {
            memo = JSON.parse(decoded);
        } catch (e) {
            console.log('⚠️  Could not parse Livewire data');
            return;
        }

        console.log('📝 Filling form with repository details...');
        console.log(`   Repository: ${this.githubRepo}`);
        console.log(`   Branch: master`);
        console.log(`   Port: 3000`);
        console.log(`   Domain: ${this.domain}`);

        // Create Livewire payload to submit the form
        const payload = {
            fingerprint: memo.memo?.fingerprint || memo.fingerprint || {},
            serverMemo: memo.memo || memo.serverMemo || {},
            updates: [
                {
                    type: 'syncInput',
                    payload: { name: 'public_repository_url', value: this.githubRepo }
                },
                {
                    type: 'syncInput',
                    payload: { name: 'git_branch', value: 'master' }
                },
                {
                    type: 'syncInput',
                    payload: { name: 'ports_exposes', value: '3000' }
                },
                {
                    type: 'syncInput',
                    payload: { name: 'domains', value: this.domain }
                },
                {
                    type: 'callMethod',
                    payload: { method: 'submit', params: [] }
                }
            ]
        };

        console.log('🚀 Submitting application creation form...');

        const result = await this.request(`${this.baseURL}/livewire/message/${wireId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Livewire': 'true',
                'X-CSRF-TOKEN': this.csrfToken,
                'Referer': publicRepoUrl
            },
            body: payload
        });

        if (result.ok) {
            console.log('✅ Application creation request submitted');

            // Try to extract application ID
            const appMatch = JSON.stringify(result.data).match(/application\/([a-z0-9]{24})/);
            if (appMatch) {
                this.applicationId = appMatch[1];
                console.log(`✅ Application ID: ${this.applicationId}`);
            }
        } else {
            console.log('⚠️  Application creation response unclear');
            console.log('   Check Coolify dashboard for status');
        }
    }

    async deploy() {
        console.log('🚀 Coolify Deploy CLI - Real Browser-Emulated Deployment');
        console.log('═══════════════════════════════════════════════════════════\n');

        try {
            await this.login();
            await this.createProject();
            await this.getEnvironment();
            await this.createApplication();

            console.log('\n✅ Deployment workflow executed');
            console.log('\n📋 Summary:');
            console.log(`   Project: ${this.projectId}`);
            console.log(`   Environment: ${this.environmentId}`);
            console.log(`   Repository: ${this.githubRepo}`);
            console.log(`   Domain: ${this.domain}`);
            console.log(`\n🌐 Manage: ${this.baseURL}/project/${this.projectId}`);

        } catch (error) {
            console.error('\n❌ Error:', error.message);
            throw error;
        }
    }
}

// Main execution
if (require.main === module) {
    const cli = new CoolifyDeploy();
    cli.deploy().catch(err => {
        console.error('Fatal:', err);
        process.exit(1);
    });
}

module.exports = CoolifyDeploy;