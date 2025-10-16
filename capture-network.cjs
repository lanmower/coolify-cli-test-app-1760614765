#!/usr/bin/env node

const { chromium } = require('playwright');

async function captureAppCreation() {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    const livewireRequests = [];

    // Capture all network requests
    page.on('request', request => {
        if (request.url().includes('/livewire')) {
            livewireRequests.push({
                url: request.url(),
                method: request.method(),
                headers: request.headers(),
                postData: request.postData()
            });
        }
    });

    page.on('response', async response => {
        if (response.url().includes('/livewire')) {
            try {
                const body = await response.text();
                console.log('\n🔍 Livewire Response:');
                console.log('URL:', response.url());
                console.log('Status:', response.status());
                console.log('Body:', body.substring(0, 500));
            } catch (e) {
                // Ignore
            }
        }
    });

    try {
        // Login
        console.log('🔐 Navigating to login...');
        await page.goto('https://coolify.acc.l-inc.co.za/login');

        await page.fill('input[type="email"]', process.env.U);
        await page.fill('input[type="password"]', process.env.P);
        await page.click('button[type="submit"]');

        await page.waitForURL('https://coolify.acc.l-inc.co.za/', { timeout: 10000 });
        console.log('✅ Logged in');

        // Navigate to new resource page
        console.log('\n📄 Navigating to new resource page...');
        await page.goto('https://coolify.acc.l-inc.co.za/project/mcssok0k4s00kc0sg4g4ow0o/environment/i0kog8s80kw04gwo4gsskk08/new');

        await page.waitForTimeout(2000);

        // Search for public repository
        console.log('🔍 Searching for public repository...');
        await page.fill('input[placeholder*="search"]', 'public');
        await page.waitForTimeout(500);

        // Click Public Repository
        console.log('🖱️  Clicking Public Repository...');
        await page.click('text=Public Repository');

        await page.waitForTimeout(2000);

        console.log('\n📝 Current URL:', page.url());

        // Fill in the form
        console.log('\n📝 Filling in repository form...');

        // Find and fill repository URL
        await page.fill('input[name="public_repository_url"]', 'https://github.com/lanmower/coolify-cli-test-app-1760614765');
        await page.waitForTimeout(500);

        await page.fill('input[name="git_branch"]', 'master');
        await page.waitForTimeout(500);

        await page.fill('input[name="ports_exposes"]', '3000');
        await page.waitForTimeout(500);

        await page.fill('input[name="domains"]', 'coolify-cli-test-app.acc.l-inc.co.za');
        await page.waitForTimeout(500);

        console.log('✅ Form filled');

        // Submit the form
        console.log('\n🚀 Submitting form...');
        await page.click('button[type="submit"]');

        // Wait for response
        await page.waitForTimeout(3000);

        console.log('\n📊 Captured Livewire Requests:');
        livewireRequests.forEach((req, i) => {
            console.log(`\n--- Request ${i + 1} ---`);
            console.log('URL:', req.url);
            console.log('Method:', req.method);
            if (req.postData) {
                console.log('POST Data:', req.postData.substring(0, 1000));
            }
        });

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        console.log('\n⏸️  Pausing browser for inspection (press Ctrl+C to exit)...');
        await page.waitForTimeout(60000);
        await browser.close();
    }
}

if (!process.env.U || !process.env.P) {
    console.error('Please set U and P environment variables');
    process.exit(1);
}

captureAppCreation();
