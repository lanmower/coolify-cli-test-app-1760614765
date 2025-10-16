#!/usr/bin/env node

const { chromium } = require('playwright');
const fs = require('fs');

async function captureAll() {
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();

    const allRequests = [];

    page.on('request', request => {
        if (request.url().includes('/livewire/update') && request.method() === 'POST') {
            const postData = request.postData();
            allRequests.push({
                timestamp: new Date().toISOString(),
                url: request.url(),
                headers: request.headers(),
                postData: postData,
                postDataLength: postData ? postData.length : 0
            });
        }
    });

    console.log('🔐 Login...');
    await page.goto('https://coolify.acc.l-inc.co.za/login');
    await page.fill('input[type="email"]', process.env.U);
    await page.fill('input[type="password"]', process.env.P);
    await page.click('button[type="submit"]');
    await page.waitForURL(/coolify.acc.l-inc.co.za\/$/, { timeout: 10000 });

    console.log('📄 Navigate to form...');
    await page.goto('https://coolify.acc.l-inc.co.za/project/mcssok0k4s00kc0sg4g4ow0o/environment/i0kog8s80kw04gwo4gsskk08/new?type=public&destination=mks0ss0wkgko0c8cocogssoc&server_id=0');

    await page.waitForTimeout(3000);

    console.log('📝 Filling form...');
    try {
        // Try different selectors
        await page.fill('[name="public_repository_url"]', 'https://github.com/lanmower/coolify-cli-test-app-1760614765', { timeout: 5000 });
    } catch {}

    try {
        await page.fill('[name="git_branch"]', 'master', { timeout: 2000 });
    } catch {}

    try {
        await page.fill('[name="ports_exposes"]', '3000', { timeout: 2000 });
    } catch {}

    try {
        await page.fill('[name="domains"]', 'coolify-cli-test-app.acc.l-inc.co.za', { timeout: 2000 });
    } catch {}

    console.log('🚀 Clicking submit...');
    try {
        await page.click('button[type="submit"]', { timeout: 5000 });
    } catch {}

    console.log('⏳ Waiting for requests...');
    await page.waitForTimeout(5000);

    console.log(`\n📊 Captured ${allRequests.length} Livewire POST requests`);

    // Save all requests
    fs.writeFileSync('all-livewire-requests.json', JSON.stringify(allRequests, null, 2));
    console.log('💾 Saved to all-livewire-requests.json');

    // Show summary
    allRequests.forEach((req, i) => {
        console.log(`\n${i + 1}. [${req.timestamp}] Length: ${req.postDataLength}`);
        if (req.postData) {
            const preview = req.postData.substring(0, 200);
            console.log(`   ${preview}...`);
        }
    });

    await browser.close();
}

captureAll().catch(console.error);
